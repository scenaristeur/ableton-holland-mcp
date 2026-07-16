# AbletonMCP/init.py
from __future__ import absolute_import, print_function, unicode_literals

from _Framework.ControlSurface import ControlSurface
import importlib
import os
import socket
import json
import sys
import threading
import time
import traceback

# Change queue import for Python 2
try:
    import Queue as queue  # Python 2
except ImportError:
    import queue  # Python 3

# Constants for socket communication
DEFAULT_PORT = 9877
HOST = "0.0.0.0"


def create_instance(c_instance):
    """Create and return the AbletonMCP script instance"""
    return AbletonMCP(c_instance)


class AbletonMCP(ControlSurface):
    """AbletonMCP Remote Script for Ableton Live"""

    def __init__(self, c_instance):
        """Initialize the control surface"""
        ControlSurface.__init__(self, c_instance)
        self.log_message("AbletonMCP Remote Script initializing...")

        # Socket server for communication
        self.server = None
        self.client_threads = []
        self.server_thread = None
        self.running = False

        # Cache the song reference for easier access
        self._song = self.song()

        # Start the socket server
        self.start_server()

        self.log_message("AbletonMCP initialized")

        # Show a message in Ableton
        self.show_message(
            "AbletonMCP: Listening for commands on port " + str(DEFAULT_PORT)
        )

    def disconnect(self):
        """Called when Ableton closes or the control surface is removed"""
        self.log_message("AbletonMCP disconnecting...")
        self.running = False

        # Stop the server
        if self.server:
            try:
                self.server.close()
            except:
                pass

        # Wait for the server thread to exit
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(1.0)

        # Clean up any client threads
        for client_thread in self.client_threads[:]:
            if client_thread.is_alive():
                # We don't join them as they might be stuck
                self.log_message("Client thread still alive during disconnect")

        ControlSurface.disconnect(self)
        self.log_message("AbletonMCP disconnected")

    def start_server(self):
        """Start the socket server in a separate thread"""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((HOST, DEFAULT_PORT))
            self.server.listen(5)  # Allow up to 5 pending connections

            self.running = True
            self.server_thread = threading.Thread(target=self._server_thread)
            self.server_thread.daemon = True
            self.server_thread.start()

            self.log_message("Server started on port " + str(DEFAULT_PORT))
        except Exception as e:
            self.log_message("Error starting server: " + str(e))
            self.show_message("AbletonMCP: Error starting server - " + str(e))

    def _server_thread(self):
        """Server thread implementation - handles client connections"""
        try:
            self.log_message("Server thread started")
            # Set a timeout to allow regular checking of running flag
            self.server.settimeout(1.0)

            while self.running:
                try:
                    # Accept connections with timeout
                    client, address = self.server.accept()
                    self.log_message("Connection accepted from " + str(address))
                    self.show_message("AbletonMCP: Client connected")

                    # Handle client in a separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client, args=(client,)
                    )
                    client_thread.daemon = True
                    client_thread.start()

                    # Keep track of client threads
                    self.client_threads.append(client_thread)

                    # Clean up finished client threads
                    self.client_threads = [
                        t for t in self.client_threads if t.is_alive()
                    ]

                except socket.timeout:
                    # No connection yet, just continue
                    continue
                except Exception as e:
                    if self.running:  # Only log if still running
                        self.log_message("Server accept error: " + str(e))
                    time.sleep(0.5)

            self.log_message("Server thread stopped")
        except Exception as e:
            self.log_message("Server thread error: " + str(e))

    def _handle_client(self, client):
        """Handle communication with a connected client"""
        self.log_message("Client handler started")
        client.settimeout(None)  # No timeout for client socket
        buffer = ""  # Changed from b'' to '' for Python 2

        try:
            while self.running:
                try:
                    # Receive data
                    data = client.recv(8192)

                    if not data:
                        # Client disconnected
                        self.log_message("Client disconnected")
                        break

                    # Accumulate data in buffer with explicit encoding/decoding
                    try:
                        # Python 3: data is bytes, decode to string
                        buffer += data.decode("utf-8")
                    except AttributeError:
                        # Python 2: data is already string
                        buffer += data

                    try:
                        # Try to parse command from buffer
                        command = json.loads(buffer)  # Removed decode('utf-8')
                        buffer = ""  # Clear buffer after successful parse

                        self.log_message(
                            "Received command: " + str(command.get("type", "unknown"))
                        )

                        # Process the command and get response
                        response = self._process_command(command)

                        # Send the response with explicit encoding
                        try:
                            # Python 3: encode string to bytes
                            client.sendall(json.dumps(response).encode("utf-8"))
                        except AttributeError:
                            # Python 2: string is already bytes
                            client.sendall(json.dumps(response))
                    except ValueError:
                        # Incomplete data, wait for more
                        continue

                except Exception as e:
                    self.log_message("Error handling client data: " + str(e))
                    self.log_message(traceback.format_exc())

                    # Send error response if possible
                    error_response = {"status": "error", "message": str(e)}
                    try:
                        # Python 3: encode string to bytes
                        client.sendall(json.dumps(error_response).encode("utf-8"))
                    except AttributeError:
                        # Python 2: string is already bytes
                        client.sendall(json.dumps(error_response))
                    except:
                        # If we can't send the error, the connection is probably dead
                        break

                    # For serious errors, break the loop
                    if not isinstance(e, ValueError):
                        break
        except Exception as e:
            self.log_message("Error in client handler: " + str(e))
        finally:
            try:
                client.close()
            except:
                pass
            self.log_message("Client handler stopped")

    def _process_command(self, command):
        """Process a command from the client and return a response"""
        command_type = command.get("type", "")
        params = command.get("params", {})

        # Initialize response
        response = {"status": "success", "result": {}}

        try:
            # Route the command to the appropriate handler
            if command_type == "get_session_info":
                response["result"] = self._get_session_info()
            elif command_type == "get_track_info":
                track_index = params.get("track_index", 0)
                response["result"] = self._get_track_info(track_index)
            elif command_type == "get_track_automation":
                track_index = params.get("track_index", 0)
                target = params.get("target", "volume")
                response["result"] = self._get_track_automation(track_index, target)
            elif command_type == "reload":
                self.log_message("Reloading Remote Script module...")
                try:
                    new_mod = importlib.reload(sys.modules[__name__])
                    self.__class__ = new_mod.AbletonMCP
                    self.log_message("Remote Script reloaded OK")
                    response["result"] = {"reloaded": True}
                except Exception as e:
                    self.log_message("Reload failed: " + str(e))
                    response["status"] = "error"
                    response["message"] = "Reload failed: " + str(e)
            # Commands that modify Live's state should be scheduled on the main thread
            elif command_type in [
                "create_midi_track",
                "set_track_name",
                "create_clip",
                "create_audio_clip",
                "add_notes_to_clip",
                "set_clip_name",
                "set_tempo",
                "fire_clip",
                "stop_clip",
                "start_playback",
                "start_playback_at",
                "stop_playback",
                "load_instrument_or_effect",
                "load_browser_item",
                # Arrangement view – must run on the main thread
                "switch_to_arrangement_view",
                "set_current_song_time",
                "duplicate_session_clip_to_arrangement",
                "set_arrangement_clip_notes",
                "set_arrangement_clip_name",
                # Device parameters
                "set_device_parameter",
                "delete_device",
                # Clip operations
                "delete_session_clip",
                "delete_arrangement_clip",
                "duplicate_session_clip",
                # Scenes
                "create_scene",
                "fire_scene",
                # Mixer
                "set_send",
                "set_monitoring",
                # Project
                "freeze_track",
                "flatten_track",
                "save_project",
                "undo",
                "redo",
                # New features
                "delete_track",
                "duplicate_track",
                "duplicate_clip",
                "quantize_clip",
                "select_track",
                "set_track_color",
                "set_clip_color",
                "set_metronome",
                "set_session_record",
                "nudge_up",
                "nudge_down",
                "set_signature",
                "set_crossfader",
                "set_groove_amount",
                # System / Monitoring
                "set_tempo_follower",
                # Routing
                "set_track_input_routing",
                "set_track_output_routing",
                # Master
                "set_master_volume",
                "set_master_panning",
                "set_master_device_parameter",
                "load_browser_item_on_master",
                # Clip envelopes (modulation)
                "get_clip_envelope",
                "set_clip_envelope",
                "set_arrangement_clip_envelope",
                "set_automation_curve",
                "set_track_volume",
                "set_track_solo",
                "set_track_mute",
                "set_arrangement_clip_gain",
                "set_arrangement_clip_pitch",
                "set_arrangement_clip_warp",
                "set_arrangement_clip_markers",
                "set_arrangement_clip_name",
                # Extended device management
                "enable_device",
                "disable_device",
                "navigate_device_preset",
                # Track mixer
                "set_track_panning",
                # View control
                "set_ableton_view",
                "control_arrangement_view",
                # Cue points
                "create_cue_point",
                "delete_cue_point",
                "jump_to_cue_point",
                # Arrangement
                "set_arrangement_loop",
                "create_arrangement_midi_clip",
                "create_arrangement_audio_clip",
                "duplicate_clip_to_arrangement",
                # Automation management
                "manage_clip_automation",
                "add_clip_envelope_point",
                "clear_clip_envelope",
                "experiment_envelope",
                "envelope_dump",
                "test_create_event",
            ]:
                # Use a thread-safe approach with a response queue
                response_queue = queue.Queue()

                # Define a function to execute on the main thread
                def main_thread_task():
                    try:
                        result = None
                        if command_type == "create_midi_track":
                            index = params.get("index", -1)
                            result = self._create_midi_track(index)
                        elif command_type == "set_track_name":
                            track_index = params.get("track_index", 0)
                            name = params.get("name", "")
                            result = self._set_track_name(track_index, name)
                        elif command_type == "create_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            length = params.get("length", 4.0)
                            result = self._create_clip(track_index, clip_index, length)
                        elif command_type == "create_audio_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            path = params.get("path", "")
                            result = self._create_audio_clip(
                                track_index, clip_index, path
                            )
                        elif command_type == "add_notes_to_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            notes = params.get("notes", [])
                            result = self._add_notes_to_clip(
                                track_index, clip_index, notes
                            )
                        elif command_type == "set_clip_name":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            name = params.get("name", "")
                            result = self._set_clip_name(track_index, clip_index, name)
                        elif command_type == "set_tempo":
                            tempo = params.get("tempo", 120.0)
                            result = self._set_tempo(tempo)
                        elif command_type == "fire_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            result = self._fire_clip(track_index, clip_index)
                        elif command_type == "stop_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            result = self._stop_clip(track_index, clip_index)
                        elif command_type == "start_playback":
                            result = self._start_playback()
                        elif command_type == "start_playback_at":
                            time_val = params.get("time", 0.0)
                            result = self._start_playback_at(time_val)
                        elif command_type == "stop_playback":
                            result = self._stop_playback()
                        elif command_type == "load_instrument_or_effect":
                            track_index = params.get("track_index", 0)
                            uri = params.get("uri", "")
                            result = self._load_instrument_or_effect(track_index, uri)
                        elif command_type == "load_browser_item":
                            track_index = params.get("track_index", 0)
                            item_uri = params.get("item_uri", "")
                            result = self._load_browser_item(track_index, item_uri)
                        # ── Arrangement view commands ──────────────────────────────
                        elif command_type == "switch_to_arrangement_view":
                            result = self._switch_to_arrangement_view()
                        elif command_type == "set_current_song_time":
                            time_val = params.get("time", 0.0)
                            result = self._set_current_song_time(time_val)
                        elif command_type == "duplicate_session_clip_to_arrangement":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            destination_time = params.get("destination_time", 0.0)
                            result = self._duplicate_session_clip_to_arrangement(
                                track_index, clip_index, destination_time
                            )
                        elif command_type == "set_arrangement_clip_notes":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            notes = params.get("notes", [])
                            result = self._set_arrangement_clip_notes(
                                track_index, clip_index, notes
                            )
                        # ── Device parameters ─────────────────────────────────────
                        elif command_type == "set_device_parameter":
                            track_index = params.get("track_index", 0)
                            device_index = params.get("device_index", 0)
                            parameter_name = params.get("parameter_name", "")
                            value = params.get("value", 0.0)
                            result = self._set_device_parameter(
                                track_index, device_index, parameter_name, value
                            )
                        elif command_type == "delete_device":
                            track_index = params.get("track_index", 0)
                            device_index = params.get("device_index", 0)
                            result = self._delete_device(track_index, device_index)
                        # ── Clip operations ───────────────────────────────────────
                        elif command_type == "delete_session_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            result = self._delete_session_clip(track_index, clip_index)
                        elif command_type == "delete_arrangement_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            result = self._delete_arrangement_clip(
                                track_index, clip_index
                            )
                        elif command_type == "duplicate_session_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            dest_track = params.get("destination_track", None)
                            dest_slot = params.get("destination_slot", None)
                            result = self._duplicate_session_clip(
                                track_index, clip_index, dest_track, dest_slot
                            )
                        # ── Scenes ─────────────────────────────────────────────────
                        elif command_type == "create_scene":
                            index = params.get("index", -1)
                            result = self._create_scene(index)
                        elif command_type == "fire_scene":
                            index = params.get("index", 0)
                            result = self._fire_scene(index)
                        # ── Mixer ──────────────────────────────────────────────────
                        elif command_type == "set_send":
                            track_index = params.get("track_index", 0)
                            send_index = params.get("send_index", 0)
                            value = params.get("value", 0.0)
                            result = self._set_send(track_index, send_index, value)
                        elif command_type == "set_monitoring":
                            track_index = params.get("track_index", 0)
                            state = params.get("state", 0)
                            result = self._set_monitoring(track_index, state)
                        # ── Project ────────────────────────────────────────────────
                        elif command_type == "freeze_track":
                            track_index = params.get("track_index", 0)
                            result = self._freeze_track(track_index)
                        elif command_type == "flatten_track":
                            track_index = params.get("track_index", 0)
                            result = self._flatten_track(track_index)
                        elif command_type == "save_project":
                            result = self._save_project()
                        elif command_type == "undo":
                            result = self._undo()
                        elif command_type == "redo":
                            result = self._redo()
                        # ── New features ──────────────────────────────────────
                        elif command_type == "delete_track":
                            track_index = params.get("track_index", 0)
                            result = self._delete_track(track_index)
                        elif command_type == "duplicate_track":
                            track_index = params.get("track_index", 0)
                            result = self._duplicate_track(track_index)
                        elif command_type == "duplicate_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            result = self._duplicate_clip(track_index, clip_index)
                        elif command_type == "quantize_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            amount = params.get("amount", 1.0)
                            quantize_to = params.get("quantize_to", 2)
                            result = self._quantize_clip(
                                track_index, clip_index, amount, quantize_to
                            )
                        elif command_type == "select_track":
                            track_index = params.get("track_index", 0)
                            result = self._select_track(track_index)
                        elif command_type == "set_track_color":
                            track_index = params.get("track_index", 0)
                            color = params.get("color", 0)
                            result = self._set_track_color(track_index, color)
                        elif command_type == "set_clip_color":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            color = params.get("color", 0)
                            result = self._set_clip_color(
                                track_index, clip_index, color
                            )
                        elif command_type == "set_metronome":
                            value = params.get("value", False)
                            result = self._set_metronome(value)
                        elif command_type == "set_session_record":
                            value = params.get("value", False)
                            result = self._set_session_record(value)
                        elif command_type == "nudge_up":
                            result = self._nudge_up()
                        elif command_type == "nudge_down":
                            result = self._nudge_down()
                        elif command_type == "set_signature":
                            numerator = params.get("numerator", 4)
                            denominator = params.get("denominator", 4)
                            result = self._set_signature(numerator, denominator)
                        elif command_type == "set_crossfader":
                            value = params.get("value", 0.5)
                            result = self._set_crossfader(value)
                        elif command_type == "set_groove_amount":
                            amount = params.get("amount", 0.0)
                            result = self._set_groove_amount(amount)
                        elif command_type == "set_tempo_follower":
                            enabled = params.get("enabled", False)
                            result = self._set_tempo_follower(enabled)
                        elif command_type == "set_track_input_routing":
                            track_index = params.get("track_index", 0)
                            routing_type = params.get("routing_type", "")
                            channel = params.get("channel", None)
                            result = self._set_track_input_routing(
                                track_index, routing_type, channel
                            )
                        elif command_type == "set_track_output_routing":
                            track_index = params.get("track_index", 0)
                            routing_type = params.get("routing_type", "")
                            channel = params.get("channel", None)
                            result = self._set_track_output_routing(
                                track_index, routing_type, channel
                            )
                        elif command_type == "set_master_volume":
                            value = params.get("value", 0.85)
                            result = self._set_master_volume(value)
                        elif command_type == "set_master_panning":
                            value = params.get("value", 0.0)
                            result = self._set_master_panning(value)
                        elif command_type == "set_master_device_parameter":
                            device_index = params.get("device_index", 0)
                            parameter_name = params.get("parameter_name", "")
                            value = params.get("value", 0.0)
                            result = self._set_master_device_parameter(
                                device_index, parameter_name, value
                            )
                        elif command_type == "load_browser_item_on_master":
                            item_uri = params.get("uri", "")
                            result = self._load_browser_item_on_master(item_uri)
                        elif command_type == "set_track_volume":
                            track_index = params.get("track_index", 0)
                            value = params.get("value", 0.85)
                            result = self._set_track_volume(track_index, value)
                        # ── Clip Envelopes (modulation) ─────────────────────────
                        elif command_type == "get_clip_envelope":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            target = params.get("target", "volume")
                            is_arrangement = params.get("is_arrangement", True)
                            result = self._get_clip_envelope(
                                track_index, clip_index, target, is_arrangement
                            )
                        elif command_type == "set_clip_envelope":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            target = params.get("target", "volume")
                            points = params.get("points", [])
                            result = self._set_clip_envelope(
                                track_index, clip_index, target, points
                            )
                        elif command_type == "set_arrangement_clip_envelope":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            target = params.get("target", "volume")
                            points = params.get("points", [])
                            result = self._set_arrangement_clip_envelope(
                                track_index, clip_index, target, points
                            )
                        elif command_type == "set_automation_curve":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            target = params.get("target", "volume")
                            points = params.get("points", [])
                            is_arrangement = params.get("is_arrangement", False)
                            result = self._set_automation_curve(
                                track_index, clip_index, target, points, is_arrangement
                            )
                        elif command_type == "debug_clip_envelopes":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            is_arrangement = params.get("is_arrangement", True)
                            result = self._debug_clip_envelopes(
                                track_index, clip_index, is_arrangement
                            )
                        elif command_type == "set_track_solo":
                            track_index = params.get("track_index", 0)
                            solo = params.get("solo", False)
                            result = self._set_track_solo(track_index, solo)
                        elif command_type == "set_track_mute":
                            track_index = params.get("track_index", 0)
                            mute = params.get("mute", False)
                            result = self._set_track_mute(track_index, mute)
                        elif command_type == "set_arrangement_clip_gain":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            gain = params.get("gain", 0.0)
                            result = self._set_arrangement_clip_gain(
                                track_index, clip_index, gain
                            )
                        elif command_type == "set_arrangement_clip_pitch":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            coarse = params.get("coarse", 0)
                            fine = params.get("fine", 0)
                            result = self._set_arrangement_clip_pitch(
                                track_index, clip_index, coarse, fine
                            )
                        elif command_type == "set_arrangement_clip_warp":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            warp_on = params.get("warp_on", True)
                            warp_mode = params.get("warp_mode", 0)
                            result = self._set_arrangement_clip_warp(
                                track_index, clip_index, warp_on, warp_mode
                            )
                        elif command_type == "set_arrangement_clip_markers":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            start_marker = params.get("start_marker", 0.0)
                            end_marker = params.get("end_marker", 0.0)
                            result = self._set_arrangement_clip_markers(
                                track_index, clip_index, start_marker, end_marker
                            )
                        elif command_type == "set_arrangement_clip_name":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            name = params.get("name", "")
                            result = self._set_arrangement_clip_name(
                                track_index, clip_index, name
                            )
                        # ── Extended device management ────────────────────────────
                        elif command_type == "enable_device":
                            track_index = params.get("track_index", 0)
                            device_index = params.get("device_index", 0)
                            device_name = params.get("device_name", "")
                            chain_index = params.get("chain_index", 0)
                            result = self._enable_device(
                                track_index, device_index, device_name, chain_index
                            )
                        elif command_type == "disable_device":
                            track_index = params.get("track_index", 0)
                            device_index = params.get("device_index", 0)
                            device_name = params.get("device_name", "")
                            chain_index = params.get("chain_index", 0)
                            result = self._disable_device(
                                track_index, device_index, device_name, chain_index
                            )
                        elif command_type == "navigate_device_preset":
                            track_index = params.get("track_index", 0)
                            device_index = params.get("device_index", 1)
                            chain_index = params.get("chain_index", 0)
                            direction = params.get("direction", "next")
                            result = self._navigate_device_preset(
                                track_index, device_index, chain_index, direction
                            )
                        # ── Track mixer ──────────────────────────────────────────
                        elif command_type == "set_track_panning":
                            track_index = params.get("track_index", 0)
                            panning = params.get("panning", 0.0)
                            result = self._set_track_panning(track_index, panning)
                        # ── View control ─────────────────────────────────────────
                        elif command_type == "set_ableton_view":
                            view = params.get("view", "Arranger")
                            result = self._set_ableton_view(view)
                        elif command_type == "control_arrangement_view":
                            action = params.get("action", "")
                            track_idx = params.get("track_index", 0)
                            result = self._control_arrangement_view(action, track_idx)
                        # ── Cue points ───────────────────────────────────────────
                        elif command_type == "create_cue_point":
                            bar = params.get("bar", 0)
                            beat = params.get("beat", 0.0)
                            name = params.get("name", "")
                            result = self._create_cue_point(bar, beat, name)
                        elif command_type == "delete_cue_point":
                            bar = params.get("bar", 0)
                            beat = params.get("beat", 0.0)
                            result = self._delete_cue_point(bar, beat)
                        elif command_type == "jump_to_cue_point":
                            direction = params.get("direction", "")
                            name = params.get("name", "")
                            result = self._jump_to_cue_point(direction, name)
                        # ── Arrangement ──────────────────────────────────────────
                        elif command_type == "set_arrangement_loop":
                            enabled = params.get("enabled", True)
                            start_bar = params.get("start_bar", 0)
                            end_bar = params.get("end_bar", 0)
                            start_beat = params.get("start_beat", 0.0)
                            length_beats = params.get("length_beats", 0.0)
                            result = self._set_arrangement_loop(
                                enabled, start_bar, end_bar, start_beat, length_beats
                            )
                        elif command_type == "create_arrangement_midi_clip":
                            track_index = params.get("track_index", 0)
                            start_bar = params.get("start_bar", 0)
                            end_bar = params.get("end_bar", 0)
                            start_beat = params.get("start_beat", 0.0)
                            length_beats = params.get("length_beats", 4.0)
                            name = params.get("name", "")
                            result = self._create_arrangement_midi_clip(
                                track_index,
                                start_bar,
                                end_bar,
                                start_beat,
                                length_beats,
                                name,
                            )
                        elif command_type == "create_arrangement_audio_clip":
                            track_index = params.get("track_index", 0)
                            file_path = params.get("file_path", "")
                            start_bar = params.get("start_bar", 0)
                            start_beat = params.get("start_beat", 0.0)
                            result = self._create_arrangement_audio_clip(
                                track_index, file_path, start_bar, start_beat
                            )
                        elif command_type == "duplicate_clip_to_arrangement":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            dest_bar = params.get("destination_bar", 0)
                            dest_beat = params.get("destination_beat", 0.0)
                            result = self._duplicate_clip_to_arrangement(
                                track_index, clip_index, dest_bar, dest_beat
                            )
                        # ── Automation management ───────────────────────────────
                        elif command_type == "manage_clip_automation":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 1)
                            clip_name = params.get("clip_name", "")
                            action = params.get("action", "create")
                            param_name = params.get("parameter_name", "volume")
                            result = self._manage_clip_automation(
                                track_index, clip_index, clip_name, action, param_name
                            )
                        elif command_type == "add_clip_envelope_point":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            target = params.get("target", "device_1_Volume")
                            time = params.get("time", 0.0)
                            value = params.get("value", 0.0)
                            duration = params.get("duration", 0.0)
                            is_arr = params.get("is_arrangement", False)
                            result = self._add_clip_envelope_point(
                                track_index,
                                clip_index,
                                target,
                                time,
                                value,
                                duration,
                                is_arr,
                            )
                        elif command_type == "clear_clip_envelope":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            target = params.get("target", "device_1_Volume")
                            is_arr = params.get("is_arrangement", False)
                            result = self._clear_clip_envelope(
                                track_index, clip_index, target, is_arr
                            )
                        elif command_type == "experiment_envelope":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            target = params.get("target", "device_1_Volume")
                            is_arr = params.get("is_arrangement", False)
                            result = self._experiment_envelope(
                                track_index, clip_index, target, is_arr
                            )
                        elif command_type == "envelope_dump":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            is_arr = params.get("is_arrangement", True)
                            result = self._envelope_dump(
                                track_index, clip_index, is_arr
                            )
                        elif command_type == "test_create_event":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            target = params.get("target", "device_1_Volume")
                            time = params.get("time", 0.0)
                            value = params.get("value", 0.0)
                            result = self._test_create_event(
                                track_index, clip_index, target, time, value
                            )

                        # Put the result in the queue
                        response_queue.put({"status": "success", "result": result})
                    except Exception as e:
                        self.log_message("Error in main thread task: " + str(e))
                        self.log_message(traceback.format_exc())
                        response_queue.put({"status": "error", "message": str(e)})

                # Schedule the task to run on the main thread
                try:
                    self.schedule_message(0, main_thread_task)
                except AssertionError:
                    # If we're already on the main thread, execute directly
                    main_thread_task()

                # Wait for the response with a timeout. Some commands (notably
                # create_audio_clip, which decodes/imports the audio file on
                # the main thread) can take longer than the default 10s on
                # larger files — give them more headroom.
                long_running_commands = {"create_audio_clip": 60.0}
                queue_timeout = long_running_commands.get(command_type, 10.0)
                try:
                    task_response = response_queue.get(timeout=queue_timeout)
                    if task_response.get("status") == "error":
                        response["status"] = "error"
                        response["message"] = task_response.get(
                            "message", "Unknown error"
                        )
                    else:
                        response["result"] = task_response.get("result", {})
                except queue.Empty:
                    response["status"] = "error"
                    response["message"] = "Timeout waiting for operation to complete"
            elif command_type == "get_device_parameters":
                track_index = params.get("track_index", 0)
                device_index = params.get("device_index", 0)
                response["result"] = self._get_device_parameters(
                    track_index, device_index
                )
            elif command_type == "get_clip_notes":
                track_index = params.get("track_index", 0)
                clip_index = params.get("clip_index", 0)
                response["result"] = self._get_clip_notes(track_index, clip_index)
            elif command_type == "get_sends":
                track_index = params.get("track_index", 0)
                response["result"] = self._get_sends(track_index)
            elif command_type == "get_arrangement_clip_notes":
                track_index = params.get("track_index", 0)
                clip_index = params.get("clip_index", 0)
                response["result"] = self._get_arrangement_clip_notes(
                    track_index, clip_index
                )
            elif command_type == "get_browser_item":
                uri = params.get("uri", None)
                path = params.get("path", None)
                response["result"] = self._get_browser_item(uri, path)
            elif command_type == "get_browser_categories":
                category_type = params.get("category_type", "all")
                response["result"] = self._get_browser_categories(category_type)
            elif command_type == "get_browser_items":
                path = params.get("path", "")
                item_type = params.get("item_type", "all")
                response["result"] = self._get_browser_items(path, item_type)
            # Add the new browser commands
            elif command_type == "get_browser_tree":
                category_type = params.get("category_type", "all")
                response["result"] = self.get_browser_tree(category_type)
            elif command_type == "get_browser_items_at_path":
                path = params.get("path", "")
                response["result"] = self.get_browser_items_at_path(path)
            # Read-only arrangement command – no main-thread scheduling required
            elif command_type == "get_arrangement_clips":
                track_index = params.get("track_index", 0)
                response["result"] = self._get_arrangement_clips(track_index)
            # ── Read-only new features ─────────────────────────────────────────
            elif command_type == "get_track_color":
                track_index = params.get("track_index", 0)
                response["result"] = self._get_track_color(track_index)
            elif command_type == "get_clip_color":
                track_index = params.get("track_index", 0)
                clip_index = params.get("clip_index", 0)
                response["result"] = self._get_clip_color(track_index, clip_index)
            elif command_type == "get_metronome":
                response["result"] = self._get_metronome()
            elif command_type == "get_session_record":
                response["result"] = self._get_session_record()
            elif command_type == "get_crossfader":
                response["result"] = self._get_crossfader()
            elif command_type == "get_groove_amount":
                response["result"] = self._get_groove_amount()
            # ── System / Monitoring ────────────────────────────────────────────
            elif command_type == "get_cpu_load":
                response["result"] = self._get_cpu_load()
            elif command_type == "get_live_version":
                response["result"] = self._get_live_version()
            elif command_type == "get_tempo_follower":
                response["result"] = self._get_tempo_follower()
            elif command_type == "get_control_surfaces":
                response["result"] = self._get_control_surfaces()
            # ── Routing ────────────────────────────────────────────────────────
            elif command_type == "get_track_routing":
                track_index = params.get("track_index", 0)
                response["result"] = self._get_track_routing(track_index)
            # ── Master track ───────────────────────────────────────────────────
            elif command_type == "get_master_track":
                response["result"] = self._get_master_track()
            elif command_type == "get_master_device_parameters":
                device_index = params.get("device_index", 0)
                response["result"] = self._get_master_device_parameters(device_index)
            # ── Extended read-only commands ──────────────────────────────────────
            elif command_type == "get_chain_info":
                track_index = params.get("track_index", 0)
                device_index = params.get("device_index", 1)
                chain_index = params.get("chain_index", 0)
                response["result"] = self._get_chain_info(
                    track_index, device_index, chain_index
                )
            elif command_type == "get_drum_pad_info":
                track_index = params.get("track_index", 0)
                device_index = params.get("device_index", 1)
                response["result"] = self._get_drum_pad_info(track_index, device_index)
            elif command_type == "get_cue_points":
                response["result"] = self._get_cue_points()
            elif command_type == "get_track_volume":
                track_index = params.get("track_index", 0)
                response["result"] = self._get_track_volume(track_index)
            elif command_type == "get_track_deletion_status":
                response["result"] = self._get_track_deletion_status()
            else:
                response["status"] = "error"
                response["message"] = "Unknown command: " + command_type
        except Exception as e:
            self.log_message("Error processing command: " + str(e))
            self.log_message(traceback.format_exc())
            response["status"] = "error"
            response["message"] = str(e)

        return response

    # Command implementations

    def _safe_song_property(self, attr, cast, default):
        """Read self._song.<attr> with cast, returning default on common failures.
        Catches only narrow exceptions so genuine bugs still surface."""
        try:
            return cast(getattr(self._song, attr))
        except (AttributeError, TypeError, ValueError):
            return default

    def _get_session_info(self):
        """Get information about the current session"""
        try:
            result = {
                "tempo": self._song.tempo,
                "signature_numerator": self._song.signature_numerator,
                "signature_denominator": self._song.signature_denominator,
                "track_count": len(self._song.tracks),
                "return_track_count": len(self._song.return_tracks),
                "master_track": {
                    "name": "Master",
                    "volume": self._song.master_track.mixer_device.volume.value,
                    "panning": self._song.master_track.mixer_device.panning.value,
                },
                # Transport / playback state — lets clients render a live
                # playhead without polling separately. Each property is read
                # via _safe_song_property so an attribute missing on a given
                # Live version falls back to its default rather than breaking
                # the response shape.
                "is_playing": self._safe_song_property("is_playing", bool, False),
                "current_song_time": self._safe_song_property(
                    "current_song_time", float, 0.0
                ),
                "song_length": self._safe_song_property("song_length", float, 0.0),
                "loop": self._safe_song_property("loop", bool, False),
                "loop_start": self._safe_song_property("loop_start", float, 0.0),
                "loop_length": self._safe_song_property("loop_length", float, 0.0),
            }
            return result
        except Exception as e:
            self.log_message("Error getting session info: " + str(e))
            raise

    def _get_track_info(self, track_index):
        """Get information about a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            # Get clip slots
            clip_slots = []
            for slot_index, slot in enumerate(track.clip_slots):
                clip_info = None
                if slot.has_clip:
                    clip = slot.clip
                    clip_info = {
                        "name": clip.name,
                        "length": clip.length,
                        "is_playing": clip.is_playing,
                        "is_recording": clip.is_recording,
                    }

                clip_slots.append(
                    {"index": slot_index, "has_clip": slot.has_clip, "clip": clip_info}
                )

            # Get devices
            devices = []
            for device_index, device in enumerate(track.devices):
                devices.append(
                    {
                        "index": device_index,
                        "name": device.name,
                        "class_name": device.class_name,
                        "type": self._get_device_type(device),
                    }
                )

            result = {
                "index": track_index,
                "name": track.name,
                "is_audio_track": track.has_audio_input,
                "is_midi_track": track.has_midi_input,
                "mute": track.mute,
                "solo": track.solo,
                "arm": track.arm,
                "volume": track.mixer_device.volume.value,
                "panning": track.mixer_device.panning.value,
                "clip_slots": clip_slots,
                "devices": devices,
            }
            return result
        except Exception as e:
            self.log_message("Error getting track info: " + str(e))
            raise

    def _create_midi_track(self, index):
        """Create a new MIDI track at the specified index"""
        try:
            # Create the track
            self._song.create_midi_track(index)

            # Get the new track
            new_track_index = len(self._song.tracks) - 1 if index == -1 else index
            new_track = self._song.tracks[new_track_index]

            result = {"index": new_track_index, "name": new_track.name}
            return result
        except Exception as e:
            self.log_message("Error creating MIDI track: " + str(e))
            raise

    def _set_track_name(self, track_index, name):
        """Set the name of a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            # Set the name
            track = self._song.tracks[track_index]
            track.name = name

            result = {"name": track.name}
            return result
        except Exception as e:
            self.log_message("Error setting track name: " + str(e))
            raise

    def _create_clip(self, track_index, clip_index, length):
        """Create a new MIDI clip in the specified track and clip slot"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            # Check if the clip slot already has a clip
            if clip_slot.has_clip:
                raise Exception("Clip slot already has a clip")

            # Create the clip
            clip_slot.create_clip(length)

            result = {"name": clip_slot.clip.name, "length": clip_slot.clip.length}
            return result
        except Exception as e:
            self.log_message("Error creating clip: " + str(e))
            raise

    def _create_audio_clip(self, track_index, clip_index, path):
        """Create an audio clip in the specified audio track clip slot by importing a file.

        Requires Ableton Live 12.0.5 or newer (the underlying
        ClipSlot.create_audio_clip Live API was introduced in 12.0.5 — it is
        not available in earlier 12.0.x releases).
        """
        try:
            if not path:
                raise ValueError("Audio file path is required")

            if not os.path.isabs(path):
                raise ValueError("Audio file path must be absolute (got: %s)" % path)

            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            # Must be an audio track. Audio tracks expose audio input; MIDI
            # tracks don't. Reject MIDI / return tracks up front so the caller
            # gets a clear error instead of a Live API exception.
            if getattr(track, "has_midi_input", False) or not getattr(
                track, "has_audio_input", True
            ):
                raise ValueError("Track %d is not an audio track" % track_index)

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            if clip_slot.has_clip:
                raise Exception("Clip slot already has a clip")

            if not hasattr(clip_slot, "create_audio_clip"):
                raise Exception(
                    "ClipSlot.create_audio_clip is unavailable in this Ableton Live "
                    "version. Requires Live 12.0.5 or newer."
                )

            clip_slot.create_audio_clip(path)

            result = {
                "name": clip_slot.clip.name,
                "length": clip_slot.clip.length,
                "is_audio_clip": clip_slot.clip.is_audio_clip,
            }
            return result
        except Exception as e:
            self.log_message("Error creating audio clip: " + str(e))
            raise

    def _add_notes_to_clip(self, track_index, clip_index, notes):
        """Add MIDI notes to a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            clip = clip_slot.clip

            # Convert note data to Live's format
            live_notes = []
            for note in notes:
                pitch = note.get("pitch", 60)
                start_time = note.get("start_time", 0.0)
                duration = note.get("duration", 0.25)
                velocity = note.get("velocity", 100)
                mute = note.get("mute", False)

                live_notes.append((pitch, start_time, duration, velocity, mute))

            # Add the notes
            clip.set_notes(tuple(live_notes))

            result = {"note_count": len(notes)}
            return result
        except Exception as e:
            self.log_message("Error adding notes to clip: " + str(e))
            raise

    def _set_clip_name(self, track_index, clip_index, name):
        """Set the name of a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            clip = clip_slot.clip
            clip.name = name

            result = {"name": clip.name}
            return result
        except Exception as e:
            self.log_message("Error setting clip name: " + str(e))
            raise

    def _set_tempo(self, tempo):
        """Set the tempo of the session"""
        try:
            self._song.tempo = tempo

            result = {"tempo": self._song.tempo}
            return result
        except Exception as e:
            self.log_message("Error setting tempo: " + str(e))
            raise

    def _fire_clip(self, track_index, clip_index):
        """Fire a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            clip_slot.fire()

            result = {"fired": True}
            return result
        except Exception as e:
            self.log_message("Error firing clip: " + str(e))
            raise

    def _stop_clip(self, track_index, clip_index):
        """Stop a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            clip_slot.stop()

            result = {"stopped": True}
            return result
        except Exception as e:
            self.log_message("Error stopping clip: " + str(e))
            raise

    def _start_playback(self):
        """Start playing the session"""
        try:
            self._song.start_playing()

            result = {"playing": self._song.is_playing}
            return result
        except Exception as e:
            self.log_message("Error starting playback: " + str(e))
            raise

    def _start_playback_at(self, time_val):
        """Start playback first, THEN jump to position (Live resets time on start_playing)."""
        try:
            self._song.start_playing()
            self._song.current_song_time = float(time_val)
            return {
                "current_song_time": self._song.current_song_time,
                "playing": self._song.is_playing,
            }
        except Exception as e:
            self.log_message("Error starting playback at time: " + str(e))
            raise

    def _stop_playback(self):
        """Stop playing the session"""
        try:
            self._song.stop_playing()

            result = {"playing": self._song.is_playing}
            return result
        except Exception as e:
            self.log_message("Error stopping playback: " + str(e))
            raise

    # ── Arrangement view implementations ──────────────────────────────────────

    def _switch_to_arrangement_view(self):
        """Switch Ableton's main window to the Arrangement view"""
        try:
            self.application().view.show_view("Arranger")
            return {"view": "Arranger"}
        except Exception as e:
            self.log_message("Error switching to arrangement view: " + str(e))
            raise

    def _set_current_song_time(self, time_val):
        """Move the arrangement playhead to a position in beats"""
        try:
            self._song.current_song_time = float(time_val)
            return {"current_song_time": self._song.current_song_time}
        except Exception as e:
            self.log_message("Error setting current song time: " + str(e))
            raise

    def _get_arrangement_clips(self, track_index):
        """Return all clips placed in the Arrangement timeline for a track.

        Each clip dict contains:
          name, start_time, end_time, length, color,
          is_midi_clip, is_audio_clip, is_playing,
          gain (audio clips only)
        """
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]
            clips = []

            # track.arrangement_clips is available in Live 11 / 12
            for clip in track.arrangement_clips:
                clip_info = {
                    "name": clip.name,
                    "start_time": clip.start_time,
                    "end_time": clip.end_time,
                    "length": clip.length,
                    "color": clip.color,
                    "is_midi_clip": clip.is_midi_clip,
                    "is_audio_clip": clip.is_audio_clip,
                    "is_playing": clip.is_playing,
                }
                if clip.is_audio_clip:
                    try:
                        clip_info["gain"] = clip.gain
                    except Exception:
                        clip_info["gain"] = 0.0
                    try:
                        clip_info["pitch_coarse"] = clip.pitch_coarse
                    except Exception:
                        clip_info["pitch_coarse"] = 0
                    try:
                        clip_info["pitch_fine"] = clip.pitch_fine
                    except Exception:
                        clip_info["pitch_fine"] = 0
                    try:
                        clip_info["warp_on"] = clip.warp_on
                    except Exception:
                        clip_info["warp_on"] = False
                    try:
                        clip_info["warp_mode"] = clip.warp_mode
                    except Exception:
                        clip_info["warp_mode"] = 0
                    try:
                        clip_info["start_marker"] = clip.start_marker
                    except Exception:
                        clip_info["start_marker"] = 0.0
                    try:
                        clip_info["end_marker"] = clip.end_marker
                    except Exception:
                        clip_info["end_marker"] = 0.0
                    try:
                        clip_info["loop_on"] = clip.looping
                    except Exception:
                        clip_info["loop_on"] = False
                    try:
                        clip_info["loop_start"] = clip.loop_start
                    except Exception:
                        clip_info["loop_start"] = 0.0
                    try:
                        clip_info["loop_end"] = clip.loop_end
                    except Exception:
                        clip_info["loop_end"] = 0.0
                clips.append(clip_info)

            return {
                "track_index": track_index,
                "track_name": track.name,
                "clip_count": len(clips),
                "clips": clips,
            }
        except Exception as e:
            self.log_message("Error getting arrangement clips: " + str(e))
            raise

    def _set_arrangement_clip_gain(self, track_index, clip_index, gain):
        """Set the gain (in dB) of an arrangement audio clip."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]
            clips = list(track.arrangement_clips)

            if clip_index < 0 or clip_index >= len(clips):
                raise IndexError("Arrangement clip index out of range")

            clip = clips[clip_index]
            if not clip.is_audio_clip:
                raise ValueError("Clip is not an audio clip")

            clip.gain = float(gain)

            return {
                "track_index": track_index,
                "name": clip.name,
                "gain": clip.gain,
            }
        except Exception as e:
            self.log_message("Error setting arrangement clip gain: " + str(e))
            raise

    def _set_arrangement_clip_pitch(self, track_index, clip_index, coarse, fine):
        """Set pitch of an arrangement audio clip (coarse: ±48 semitones, fine: ±50 cents)."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            clips = list(track.arrangement_clips)
            if clip_index < 0 or clip_index >= len(clips):
                raise IndexError("Arrangement clip index out of range")
            clip = clips[clip_index]
            if not clip.is_audio_clip:
                raise ValueError("Clip is not an audio clip")
            clip.pitch_coarse = int(coarse)
            clip.pitch_fine = int(fine)
            return {
                "track_index": track_index,
                "name": clip.name,
                "pitch_coarse": clip.pitch_coarse,
                "pitch_fine": clip.pitch_fine,
            }
        except Exception as e:
            self.log_message("Error setting arrangement clip pitch: " + str(e))
            raise

    def _set_arrangement_clip_warp(self, track_index, clip_index, warp_on, warp_mode=0):
        """Set warp state of an arrangement audio clip."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            clips = list(track.arrangement_clips)
            if clip_index < 0 or clip_index >= len(clips):
                raise IndexError("Arrangement clip index out of range")
            clip = clips[clip_index]
            if not clip.is_audio_clip:
                raise ValueError("Clip is not an audio clip")
            clip.warp_on = bool(warp_on)
            clip.warp_mode = int(warp_mode)
            return {
                "track_index": track_index,
                "name": clip.name,
                "warp_on": clip.warp_on,
                "warp_mode": clip.warp_mode,
            }
        except Exception as e:
            self.log_message("Error setting arrangement clip warp: " + str(e))
            raise

    def _set_arrangement_clip_markers(
        self, track_index, clip_index, start_marker, end_marker
    ):
        """Set start/end markers of an arrangement audio clip."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            clips = list(track.arrangement_clips)
            if clip_index < 0 or clip_index >= len(clips):
                raise IndexError("Arrangement clip index out of range")
            clip = clips[clip_index]
            if not clip.is_audio_clip:
                raise ValueError("Clip is not an audio clip")
            clip.start_marker = float(start_marker)
            clip.end_marker = float(end_marker)
            return {
                "track_index": track_index,
                "name": clip.name,
                "start_marker": clip.start_marker,
                "end_marker": clip.end_marker,
            }
        except Exception as e:
            self.log_message("Error setting arrangement clip markers: " + str(e))
            raise

    def _set_arrangement_clip_name(self, track_index, clip_index, name):
        """Rename an arrangement clip."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            clips = list(track.arrangement_clips)
            if clip_index < 0 or clip_index >= len(clips):
                raise IndexError("Arrangement clip index out of range")
            clip = clips[clip_index]
            clip.name = str(name)
            return {
                "track_index": track_index,
                "name": clip.name,
            }
        except Exception as e:
            self.log_message("Error setting arrangement clip name: " + str(e))
            raise

    def _duplicate_session_clip_to_arrangement(
        self, track_index, clip_index, destination_time
    ):
        """Copy a Session-view clip into the Arrangement timeline.

        Uses the real Live API:
          track.duplicate_clip_to_arrangement(clip, destination_time)

        Available in Live 11 / 12.  destination_time is in beats from the
        start of the arrangement.
        """
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip slot index out of range")

            clip_slot = track.clip_slots[clip_index]

            if not clip_slot.has_clip:
                raise Exception(
                    "No clip in slot "
                    + str(clip_index)
                    + " on track "
                    + str(track_index)
                )

            clip = clip_slot.clip

            # Duplicate to arrangement at the requested beat position
            track.duplicate_clip_to_arrangement(clip, float(destination_time))

            return {
                "success": True,
                "track_index": track_index,
                "track_name": track.name,
                "clip_name": clip.name,
                "destination_time": destination_time,
            }
        except Exception as e:
            self.log_message("Error duplicating clip to arrangement: " + str(e))
            raise

    # ── Browser implementations ───────────────────────────────────────────────

    def _get_browser_item(self, uri, path):
        """Get a browser item by URI or path"""
        try:
            # Access the application's browser instance instead of creating a new one
            app = self.application()
            if not app:
                raise RuntimeError("Could not access Live application")

            result = {"uri": uri, "path": path, "found": False}

            # Try to find by URI first if provided
            if uri:
                item = self._find_browser_item_by_uri(app.browser, uri)
                if item:
                    result["found"] = True
                    result["item"] = {
                        "name": item.name,
                        "is_folder": item.is_folder,
                        "is_device": item.is_device,
                        "is_loadable": item.is_loadable,
                        "uri": item.uri,
                    }
                    return result

            # If URI not provided or not found, try by path
            if path:
                # Parse the path and navigate to the specified item
                path_parts = path.split("/")

                # Determine the root based on the first part
                current_item = None
                if path_parts[0].lower() == "instruments":
                    current_item = app.browser.instruments
                elif path_parts[0].lower() == "sounds":
                    current_item = app.browser.sounds
                elif path_parts[0].lower() == "drums":
                    current_item = app.browser.drums
                elif path_parts[0].lower() == "audio_effects":
                    current_item = app.browser.audio_effects
                elif path_parts[0].lower() == "midi_effects":
                    current_item = app.browser.midi_effects
                else:
                    # Default to instruments if not specified
                    current_item = app.browser.instruments
                    # Don't skip the first part in this case
                    path_parts = ["instruments"] + path_parts

                # Navigate through the path
                for i in range(1, len(path_parts)):
                    part = path_parts[i]
                    if not part:  # Skip empty parts
                        continue

                    found = False
                    for child in current_item.children:
                        if child.name.lower() == part.lower():
                            current_item = child
                            found = True
                            break

                    if not found:
                        result["error"] = "Path part '{0}' not found".format(part)
                        return result

                # Found the item
                result["found"] = True
                result["item"] = {
                    "name": current_item.name,
                    "is_folder": current_item.is_folder,
                    "is_device": current_item.is_device,
                    "is_loadable": current_item.is_loadable,
                    "uri": current_item.uri,
                }

            return result
        except Exception as e:
            self.log_message("Error getting browser item: " + str(e))
            self.log_message(traceback.format_exc())
            raise

    def _load_browser_item(self, track_index, item_uri):
        """Load a browser item onto a track by its URI"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            # Access the application's browser instance instead of creating a new one
            app = self.application()

            # Find the browser item by URI
            item = self._find_browser_item_by_uri(app.browser, item_uri)

            if not item:
                raise ValueError(
                    "Browser item with URI '{0}' not found".format(item_uri)
                )

            # Select the track
            self._song.view.selected_track = track

            # Load the item
            app.browser.load_item(item)

            result = {
                "loaded": True,
                "item_name": item.name,
                "track_name": track.name,
                "uri": item_uri,
            }
            return result
        except Exception as e:
            self.log_message("Error loading browser item: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _load_instrument_or_effect(self, track_index, uri):
        """Load an instrument/effect onto a track by URI (alias for _load_browser_item)."""
        return self._load_browser_item(track_index, uri)

    # Substring markers that point a URI at a likely root. If no marker
    # matches we fall back to the default order, so this is purely an
    # optimisation — never a correctness change.
    _URI_ROOT_HINTS = (
        ("plugins", ("vst:", "vst3:", "au:", "query:plugins", "plugin#")),
        ("max_for_live", ("max for live", "maxforlive", "m4l", "query:max")),
        (
            "user_library",
            ("user library", "userlibrary", "query:user library", "query:user-library"),
        ),
        ("packs", ("query:packs", "/packs/")),
        ("samples", ("query:samples", "sample:", "/samples/")),
        ("drums", ("query:drums", "/drums/", "query:drums#")),
        (
            "instruments",
            (
                "query:instruments",
                "/instruments/",
                "query:synths#",
                "query:instruments#",
            ),
        ),
        ("sounds", ("query:sounds", "/sounds/", "query:sounds#")),
        ("audio_effects", ("query:audio effects", "audioeffects", "/audio_effects/")),
        ("midi_effects", ("query:midi effects", "midieffects", "/midi_effects/")),
    )

    def _order_roots_by_uri(self, roots, uri):
        """Reorder ``roots`` so the URI's likely root is walked first."""
        if not isinstance(uri, (bytes, str)) or not uri:
            return roots
        lowered = uri.lower()
        for attr, markers in self._URI_ROOT_HINTS:
            if any(m in lowered for m in markers):
                head = [(a, r) for (a, r) in roots if a == attr]
                tail = [(a, r) for (a, r) in roots if a != attr]
                return head + tail
        return roots

    def _find_browser_item_by_uri(
        self, browser_or_item, uri, max_depth=10, current_depth=0
    ):
        """Find a browser item by its URI.

        Top-level lookups are memoised on ``self._uri_cache`` so repeated
        loads of the same URI don't re-walk the entire browser tree.
        """
        if current_depth == 0:
            cache = getattr(self, "_uri_cache", None)
            if cache is None:
                self._uri_cache = cache = {}
            if uri in cache:
                return cache[uri]
            result = self._walk_browser_for_uri(browser_or_item, uri, max_depth, 0)
            if result is not None:
                cache[uri] = result
            return result
        return self._walk_browser_for_uri(
            browser_or_item, uri, max_depth, current_depth
        )

    def _walk_browser_for_uri(self, browser_or_item, uri, max_depth, current_depth):
        """Recursive walk used by :py:meth:`_find_browser_item_by_uri`."""
        try:
            # Check if this is the item we're looking for
            if hasattr(browser_or_item, "uri") and browser_or_item.uri == uri:
                return browser_or_item

            # Stop recursion if we've reached max depth
            if current_depth >= max_depth:
                return None

            # Check if this is a browser with root categories
            if hasattr(browser_or_item, "instruments"):
                roots = [
                    ("instruments", browser_or_item.instruments),
                    ("sounds", browser_or_item.sounds),
                    ("drums", browser_or_item.drums),
                    ("audio_effects", browser_or_item.audio_effects),
                    ("midi_effects", browser_or_item.midi_effects),
                ]
                for extra_attr in (
                    "plugins",
                    "max_for_live",
                    "user_library",
                    "packs",
                    "samples",
                ):
                    if hasattr(browser_or_item, extra_attr):
                        try:
                            roots.append(
                                (extra_attr, getattr(browser_or_item, extra_attr))
                            )
                        except (AttributeError, RuntimeError) as e:
                            self.log_message(
                                "Could not access browser.{0}: {1}".format(
                                    extra_attr, str(e)
                                )
                            )

                for _attr, category in self._order_roots_by_uri(roots, uri):
                    item = self._find_browser_item_by_uri(
                        category, uri, max_depth, current_depth + 1
                    )
                    if item:
                        return item

                return None

            # Check if this item has children
            if hasattr(browser_or_item, "children") and browser_or_item.children:
                for child in browser_or_item.children:
                    item = self._find_browser_item_by_uri(
                        child, uri, max_depth, current_depth + 1
                    )
                    if item:
                        return item

            return None
        except Exception as e:
            self.log_message("Error finding browser item by URI: {0}".format(str(e)))
            return None

    # Helper methods

    def _get_device_type(self, device):
        """Get the type of a device"""
        try:
            # Simple heuristic - in a real implementation you'd look at the device class
            if device.can_have_drum_pads:
                return "drum_machine"
            elif device.can_have_chains:
                return "rack"
            elif "instrument" in device.class_display_name.lower():
                return "instrument"
            elif "audio_effect" in device.class_name.lower():
                return "audio_effect"
            elif "midi_effect" in device.class_name.lower():
                return "midi_effect"
            else:
                return "unknown"
        except:
            return "unknown"

    def get_browser_tree(self, category_type="all"):
        """
        Get a simplified tree of browser categories.

        Args:
            category_type: Type of categories to get ('all', 'instruments', 'sounds', etc.)

        Returns:
            Dictionary with the browser tree structure
        """
        try:
            # Access the application's browser instance instead of creating a new one
            app = self.application()
            if not app:
                raise RuntimeError("Could not access Live application")

            # Check if browser is available
            if not hasattr(app, "browser") or app.browser is None:
                raise RuntimeError("Browser is not available in the Live application")

            # Log available browser attributes to help diagnose issues
            browser_attrs = [
                attr for attr in dir(app.browser) if not attr.startswith("_")
            ]
            self.log_message("Available browser attributes: {0}".format(browser_attrs))

            result = {
                "type": category_type,
                "categories": [],
                "available_categories": browser_attrs,
            }

            # Helper function to process a browser item and its children
            def process_item(item, depth=0):
                if not item:
                    return None

                result = {
                    "name": item.name if hasattr(item, "name") else "Unknown",
                    "is_folder": hasattr(item, "children") and bool(item.children),
                    "is_device": hasattr(item, "is_device") and item.is_device,
                    "is_loadable": hasattr(item, "is_loadable") and item.is_loadable,
                    "uri": item.uri if hasattr(item, "uri") else None,
                    "children": [],
                }

                return result

            # Process based on category type and available attributes
            if (category_type == "all" or category_type == "instruments") and hasattr(
                app.browser, "instruments"
            ):
                try:
                    instruments = process_item(app.browser.instruments)
                    if instruments:
                        instruments["name"] = "Instruments"  # Ensure consistent naming
                        result["categories"].append(instruments)
                except Exception as e:
                    self.log_message("Error processing instruments: {0}".format(str(e)))

            if (category_type == "all" or category_type == "sounds") and hasattr(
                app.browser, "sounds"
            ):
                try:
                    sounds = process_item(app.browser.sounds)
                    if sounds:
                        sounds["name"] = "Sounds"  # Ensure consistent naming
                        result["categories"].append(sounds)
                except Exception as e:
                    self.log_message("Error processing sounds: {0}".format(str(e)))

            if (category_type == "all" or category_type == "drums") and hasattr(
                app.browser, "drums"
            ):
                try:
                    drums = process_item(app.browser.drums)
                    if drums:
                        drums["name"] = "Drums"  # Ensure consistent naming
                        result["categories"].append(drums)
                except Exception as e:
                    self.log_message("Error processing drums: {0}".format(str(e)))

            if (category_type == "all" or category_type == "audio_effects") and hasattr(
                app.browser, "audio_effects"
            ):
                try:
                    audio_effects = process_item(app.browser.audio_effects)
                    if audio_effects:
                        audio_effects["name"] = (
                            "Audio Effects"  # Ensure consistent naming
                        )
                        result["categories"].append(audio_effects)
                except Exception as e:
                    self.log_message(
                        "Error processing audio_effects: {0}".format(str(e))
                    )

            if (category_type == "all" or category_type == "midi_effects") and hasattr(
                app.browser, "midi_effects"
            ):
                try:
                    midi_effects = process_item(app.browser.midi_effects)
                    if midi_effects:
                        midi_effects["name"] = "MIDI Effects"
                        result["categories"].append(midi_effects)
                except Exception as e:
                    self.log_message(
                        "Error processing midi_effects: {0}".format(str(e))
                    )

            # Try to process other potentially available categories
            for attr in browser_attrs:
                if attr not in [
                    "instruments",
                    "sounds",
                    "drums",
                    "audio_effects",
                    "midi_effects",
                ] and (category_type == "all" or category_type == attr):
                    try:
                        item = getattr(app.browser, attr)
                        if hasattr(item, "children") or hasattr(item, "name"):
                            category = process_item(item)
                            if category:
                                category["name"] = attr.capitalize()
                                result["categories"].append(category)
                    except Exception as e:
                        self.log_message(
                            "Error processing {0}: {1}".format(attr, str(e))
                        )

            self.log_message(
                "Browser tree generated for {0} with {1} root categories".format(
                    category_type, len(result["categories"])
                )
            )
            return result

        except Exception as e:
            self.log_message("Error getting browser tree: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def get_browser_items_at_path(self, path):
        """
        Get browser items at a specific path.

        Args:
            path: Path in the format "category/folder/subfolder"
                 where category is one of: instruments, sounds, drums, audio_effects, midi_effects
                 or any other available browser category

        Returns:
            Dictionary with items at the specified path
        """
        try:
            # Access the application's browser instance instead of creating a new one
            app = self.application()
            if not app:
                raise RuntimeError("Could not access Live application")

            # Check if browser is available
            if not hasattr(app, "browser") or app.browser is None:
                raise RuntimeError("Browser is not available in the Live application")

            # Log available browser attributes to help diagnose issues
            browser_attrs = [
                attr for attr in dir(app.browser) if not attr.startswith("_")
            ]
            self.log_message("Available browser attributes: {0}".format(browser_attrs))

            # Parse the path
            path_parts = path.split("/")
            if not path_parts:
                raise ValueError("Invalid path")

            # Determine the root category
            root_category = path_parts[0].lower()
            current_item = None

            # Check standard categories first
            if root_category == "instruments" and hasattr(app.browser, "instruments"):
                current_item = app.browser.instruments
            elif root_category == "sounds" and hasattr(app.browser, "sounds"):
                current_item = app.browser.sounds
            elif root_category == "drums" and hasattr(app.browser, "drums"):
                current_item = app.browser.drums
            elif root_category == "audio_effects" and hasattr(
                app.browser, "audio_effects"
            ):
                current_item = app.browser.audio_effects
            elif root_category == "midi_effects" and hasattr(
                app.browser, "midi_effects"
            ):
                current_item = app.browser.midi_effects
            else:
                # Try to find the category in other browser attributes
                found = False
                for attr in browser_attrs:
                    if attr.lower() == root_category:
                        try:
                            current_item = getattr(app.browser, attr)
                            found = True
                            break
                        except Exception as e:
                            self.log_message(
                                "Error accessing browser attribute {0}: {1}".format(
                                    attr, str(e)
                                )
                            )

                if not found:
                    # If we still haven't found the category, return available categories
                    return {
                        "path": path,
                        "error": "Unknown or unavailable category: {0}".format(
                            root_category
                        ),
                        "available_categories": browser_attrs,
                        "items": [],
                    }

            # Navigate through the path
            for i in range(1, len(path_parts)):
                part = path_parts[i]
                if not part:  # Skip empty parts
                    continue

                if not hasattr(current_item, "children"):
                    return {
                        "path": path,
                        "error": "Item at '{0}' has no children".format(
                            "/".join(path_parts[:i])
                        ),
                        "items": [],
                    }

                found = False
                for child in current_item.children:
                    if hasattr(child, "name") and child.name.lower() == part.lower():
                        current_item = child
                        found = True
                        break

                if not found:
                    return {
                        "path": path,
                        "error": "Path part '{0}' not found".format(part),
                        "items": [],
                    }

            # Get items at the current path
            items = []
            if hasattr(current_item, "children"):
                for child in current_item.children:
                    item_info = {
                        "name": child.name if hasattr(child, "name") else "Unknown",
                        "is_folder": hasattr(child, "children")
                        and bool(child.children),
                        "is_device": hasattr(child, "is_device") and child.is_device,
                        "is_loadable": hasattr(child, "is_loadable")
                        and child.is_loadable,
                        "uri": child.uri if hasattr(child, "uri") else None,
                    }
                    items.append(item_info)

            result = {
                "path": path,
                "name": current_item.name
                if hasattr(current_item, "name")
                else "Unknown",
                "uri": current_item.uri if hasattr(current_item, "uri") else None,
                "is_folder": hasattr(current_item, "children")
                and bool(current_item.children),
                "is_device": hasattr(current_item, "is_device")
                and current_item.is_device,
                "is_loadable": hasattr(current_item, "is_loadable")
                and current_item.is_loadable,
                "items": items,
            }

            self.log_message(
                "Retrieved {0} items at path: {1}".format(len(items), path)
            )
            return result

        except Exception as e:
            self.log_message("Error getting browser items at path: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    # ═══════════════════════════════════════════════════════════════
    # Device Parameters
    # ═══════════════════════════════════════════════════════════════

    def _get_device_parameters(self, track_index, device_index):
        """Read all parameters of a device"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]
            parameters = []
            for param in device.parameters:
                p = {
                    "name": param.name,
                    "value": param.value,
                    "min": param.min,
                    "max": param.max,
                    "is_quantized": param.is_quantized,
                }
                if param.is_quantized and hasattr(param, "value_items"):
                    try:
                        p["value_items"] = list(param.value_items)
                    except Exception:
                        p["value_items"] = None
                else:
                    p["value_items"] = None
                parameters.append(p)
            return {
                "device_name": device.name,
                "device_class": device.class_name,
                "parameters": parameters,
            }
        except Exception as e:
            self.log_message("Error getting device parameters: " + str(e))
            raise

    def _set_device_parameter(self, track_index, device_index, parameter_name, value):
        """Set a device parameter value"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]
            for param in device.parameters:
                if (
                    param.name == parameter_name
                    and hasattr(param, "value")
                    and not getattr(param, "is_enabled", False) == False
                ):
                    # Check if we can set this (some params are read-only)
                    if param.is_quantized:
                        # For quantized params, round to nearest valid index
                        param.value = int(round(value))
                    else:
                        param.value = float(value)
                    return {"name": param.name, "value": param.value}
            raise ValueError(
                "Parameter '{0}' not found or is read-only".format(parameter_name)
            )
        except Exception as e:
            self.log_message("Error setting device parameter: " + str(e))
            raise

    def _delete_device(self, track_index, device_index):
        """Delete a device from a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]
            device_name = device.name
            device_class = device.class_name
            track.delete_device(device_index)
            return {
                "deleted": True,
                "device_name": device_name,
                "device_class": device_class,
                "track_index": track_index,
                "device_index": device_index,
            }
        except Exception as e:
            self.log_message("Error deleting device: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Clip Operations
    # ═══════════════════════════════════════════════════════════════

    def _get_clip_notes(self, track_index, clip_index):
        """Read MIDI notes from a session clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip
            # Get all notes in the clip
            notes = clip.get_notes(0.0, 0, clip.length, 127)
            result_notes = []
            for note in notes:
                result_notes.append(
                    {
                        "pitch": note[0],
                        "start_time": note[1],
                        "duration": note[2],
                        "velocity": note[3],
                        "mute": note[4],
                    }
                )
            return {
                "track_index": track_index,
                "clip_name": clip.name,
                "clip_length": clip.length,
                "note_count": len(result_notes),
                "notes": result_notes,
            }
        except Exception as e:
            self.log_message("Error getting clip notes: " + str(e))
            raise

    def _delete_session_clip(self, track_index, clip_index):
        """Delete a clip from a session slot"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip_slot.delete_clip()
            return {
                "deleted": True,
                "track_index": track_index,
                "clip_index": clip_index,
            }
        except Exception as e:
            self.log_message("Error deleting session clip: " + str(e))
            raise

    def _delete_arrangement_clip(self, track_index, clip_index):
        """Delete a clip from the arrangement"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            clips = list(track.arrangement_clips)
            if clip_index < 0 or clip_index >= len(clips):
                raise IndexError("Arrangement clip index out of range")
            clip = clips[clip_index]
            clip_name = clip.name
            track.delete_clip(clip)
            return {"deleted": True, "track_index": track_index, "clip_name": clip_name}
        except Exception as e:
            self.log_message("Error deleting arrangement clip: " + str(e))
            raise

    def _duplicate_session_clip(
        self, track_index, clip_index, destination_track, destination_slot
    ):
        """Duplicate a session clip to another slot"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            clip = clip_slot.clip

            if destination_track is not None and destination_slot is not None:
                dest_track = self._song.tracks[destination_track]
                dest_slot = dest_track.clip_slots[destination_slot]
                if dest_slot.has_clip:
                    raise Exception("Destination slot already has a clip")
                # Use Live API to duplicate
                clip.duplicate_clip_to(dest_track, destination_slot)
                return {"new_track": destination_track, "new_slot": destination_slot}
            else:
                # Duplicate within same track — use the slot's duplicate method
                clip_slot.duplicate_clip_to()
                return {"duplicated": True}
        except Exception as e:
            self.log_message("Error duplicating session clip: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Scenes
    # ═══════════════════════════════════════════════════════════════

    def _create_scene(self, index):
        """Create a new scene"""
        try:
            self._song.create_scene(index)
            # Find the new scene
            if index == -1:
                scene_index = len(self._song.scenes) - 1
            else:
                scene_index = index
            scene = self._song.scenes[scene_index]
            return {"index": scene_index, "name": scene.name}
        except Exception as e:
            self.log_message("Error creating scene: " + str(e))
            raise

    def _fire_scene(self, index):
        """Fire/launch a scene"""
        try:
            if index < 0 or index >= len(self._song.scenes):
                raise IndexError("Scene index out of range")
            scene = self._song.scenes[index]
            scene.fire()
            return {"fired": True, "index": index, "name": scene.name}
        except Exception as e:
            self.log_message("Error firing scene: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Mixer: Sends & Monitoring
    # ═══════════════════════════════════════════════════════════════

    def _get_sends(self, track_index):
        """Get send levels for a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            sends = []
            for i, send in enumerate(track.mixer_device.sends):
                sends.append(
                    {
                        "index": i,
                        "name": send.name
                        if hasattr(send, "name")
                        else "Send {0}".format(i),
                        "value": send.value,
                    }
                )
            return {"track_index": track_index, "sends": sends}
        except Exception as e:
            self.log_message("Error getting sends: " + str(e))
            raise

    def _set_send(self, track_index, send_index, value):
        """Set a send level for a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if send_index < 0 or send_index >= len(track.mixer_device.sends):
                raise IndexError("Send index out of range")
            send = track.mixer_device.sends[send_index]
            send.value = float(value)
            return {"send_index": send_index, "value": send.value}
        except Exception as e:
            self.log_message("Error setting send: " + str(e))
            raise

    def _set_monitoring(self, track_index, state):
        """Set track monitoring state: 0=auto, 1=in, 2=off"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if state not in (0, 1, 2):
                raise ValueError(
                    "Monitoring state must be 0 (auto), 1 (in), or 2 (off)"
                )
            track.current_monitoring_state = state
            return {"monitoring_state": track.current_monitoring_state}
        except Exception as e:
            self.log_message("Error setting monitoring: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Project Operations
    # ═══════════════════════════════════════════════════════════════

    def _freeze_track(self, track_index):
        """Freeze a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            track.freeze()
            return {
                "frozen": True,
                "track_index": track_index,
                "track_name": track.name,
            }
        except Exception as e:
            self.log_message("Error freezing track: " + str(e))
            raise

    def _flatten_track(self, track_index):
        """Flatten a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            track.flatten()
            return {
                "flattened": True,
                "track_index": track_index,
                "track_name": track.name,
            }
        except Exception as e:
            self.log_message("Error flattening track: " + str(e))
            raise

    def _save_project(self):
        """Save the current Live project"""
        try:
            # Try save_current_song on Application (Live 11+)
            try:
                self.application().save_current_song()
                return {"saved": True}
            except AttributeError:
                pass

            # Fallback: try Song.save()
            try:
                self.song().save()
                return {"saved": True}
            except AttributeError:
                pass

            # Fallback: try save_and_or_rename
            try:
                self.song().save_and_or_rename()
                return {"saved": True, "dialog": True}
            except AttributeError:
                pass

            raise RuntimeError(
                "Save is not available via the Live API in this version. "
                "Save manually (Ctrl+S) in Live."
            )
        except Exception as e:
            self.log_message("Error saving project: " + str(e))
            raise

    def _undo(self):
        """Undo the last action"""
        try:
            self._song.undo()
            return {"performed": True}
        except Exception as e:
            self.log_message("Error undoing: " + str(e))
            raise

    def _redo(self):
        """Redo the last undone action"""
        try:
            self._song.redo()
            return {"performed": True}
        except Exception as e:
            self.log_message("Error redoing: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Arrangement Clip Notes
    # ═══════════════════════════════════════════════════════════════

    def _get_arrangement_clip_notes(self, track_index, clip_index):
        """Read MIDI notes from an arrangement clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            clips = list(track.arrangement_clips)
            if clip_index < 0 or clip_index >= len(clips):
                raise IndexError("Arrangement clip index out of range")
            clip = clips[clip_index]
            if clip.is_midi_clip:
                notes = clip.get_notes(0.0, 0, clip.length, 127)
                result_notes = []
                for note in notes:
                    result_notes.append(
                        {
                            "pitch": note[0],
                            "start_time": note[1],
                            "duration": note[2],
                            "velocity": note[3],
                            "mute": note[4],
                        }
                    )
                return {
                    "clip_name": clip.name,
                    "clip_length": clip.length,
                    "is_midi_clip": True,
                    "note_count": len(result_notes),
                    "notes": result_notes,
                }
            else:
                return {
                    "clip_name": clip.name,
                    "clip_length": clip.length,
                    "is_midi_clip": False,
                    "note_count": 0,
                    "notes": [],
                }
        except Exception as e:
            self.log_message("Error getting arrangement clip notes: " + str(e))
            raise

    def _set_arrangement_clip_notes(self, track_index, clip_index, notes):
        """Replace all MIDI notes in an arrangement clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            clips = list(track.arrangement_clips)
            if clip_index < 0 or clip_index >= len(clips):
                raise IndexError("Arrangement clip index out of range")
            clip = clips[clip_index]
            if not clip.is_midi_clip:
                raise Exception("Clip is not a MIDI clip")
            live_notes = []
            for note in notes:
                pitch = note.get("pitch", 60)
                start_time = note.get("start_time", 0.0)
                duration = note.get("duration", 0.25)
                velocity = note.get("velocity", 100)
                mute = note.get("mute", False)
                live_notes.append((pitch, start_time, duration, velocity, mute))
            clip.set_notes(tuple(live_notes))
            return {"note_count": len(notes)}
        except Exception as e:
            self.log_message("Error setting arrangement clip notes: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Track Management
    # ═══════════════════════════════════════════════════════════════

    def _delete_track(self, track_index):
        """Delete a track from the set"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            name = track.name
            self._song.delete_track(track_index)
            return {"deleted": True, "track_index": track_index, "name": name}
        except Exception as e:
            self.log_message("Error deleting track: " + str(e))
            raise

    def _duplicate_track(self, track_index):
        """Duplicate a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            self._song.duplicate_track(track_index)
            return {"duplicated": True, "track_index": track_index}
        except Exception as e:
            self.log_message("Error duplicating track: " + str(e))
            raise

    def _duplicate_clip(self, track_index, clip_index):
        """Duplicate a session clip in place (to next empty slot)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            # Find next empty slot on the same track after current
            found = False
            for i in range(clip_index + 1, len(track.clip_slots)):
                if not track.clip_slots[i].has_clip:
                    clip_slot.duplicate_clip_to(track.clip_slots[i])
                    found = True
                    return {"duplicated": True, "new_slot": i}
            if not found:
                raise Exception("No empty slot found for duplication")
            return {"duplicated": True}
        except Exception as e:
            self.log_message("Error duplicating clip: " + str(e))
            raise

    def _quantize_clip(self, track_index, clip_index, amount, quantize_to=2):
        """Quantize a MIDI clip. quantize_to: 0=1/4, 1=1/8, 2=1/16, 3=1/32. amount: 0.0–1.0."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip
            clip.quantize(int(quantize_to), float(amount))
            return {"quantized": True, "quantize_to": quantize_to, "amount": amount}
        except Exception as e:
            self.log_message("Error quantizing clip: " + str(e))
            raise

    def _select_track(self, track_index):
        """Select a track in Ableton's UI"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            self._song.view.selected_track = self._song.tracks[track_index]
            return {"selected_track": track_index}
        except Exception as e:
            self.log_message("Error selecting track: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Track / Clip Color
    # ═══════════════════════════════════════════════════════════════

    def _get_track_color(self, track_index):
        """Get a track's color index"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            return {"track_index": track_index, "color": track.color}
        except Exception as e:
            self.log_message("Error getting track color: " + str(e))
            raise

    def _set_track_color(self, track_index, color):
        """Set a track's color index (0–255)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            track.color = int(color)
            return {"track_index": track_index, "color": int(color)}
        except Exception as e:
            self.log_message("Error setting track color: " + str(e))
            raise

    def _get_clip_color(self, track_index, clip_index):
        """Get a clip's color index"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            return {
                "track_index": track_index,
                "clip_index": clip_index,
                "color": clip_slot.clip.color,
            }
        except Exception as e:
            self.log_message("Error getting clip color: " + str(e))
            raise

    def _set_clip_color(self, track_index, clip_index, color):
        """Set a clip's color index (0–255)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip_slot.clip.color = int(color)
            return {
                "track_index": track_index,
                "clip_index": clip_index,
                "color": int(color),
            }
        except Exception as e:
            self.log_message("Error setting clip color: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Transport extras
    # ═══════════════════════════════════════════════════════════════

    def _set_metronome(self, value):
        """Toggle metronome on/off"""
        try:
            self._song.metronome = bool(value)
            return {"metronome": bool(value)}
        except Exception as e:
            self.log_message("Error setting metronome: " + str(e))
            raise

    def _get_metronome(self):
        """Get metronome state"""
        try:
            return {"metronome": self._song.metronome}
        except Exception as e:
            self.log_message("Error getting metronome: " + str(e))
            raise

    def _set_session_record(self, value):
        """Toggle session record on/off"""
        try:
            self._song.session_record = bool(value)
            return {"session_record": bool(value)}
        except Exception as e:
            self.log_message("Error setting session record: " + str(e))
            raise

    def _get_session_record(self):
        """Get session record state"""
        try:
            return {"session_record": self._song.session_record}
        except Exception as e:
            self.log_message("Error getting session record: " + str(e))
            raise

    def _nudge_up(self):
        """Nudge tempo up"""
        try:
            self._song.nudge_up = True
            return {"nudged": "up"}
        except Exception as e:
            self.log_message("Error nudging up: " + str(e))
            raise

    def _nudge_down(self):
        """Nudge tempo down"""
        try:
            self._song.nudge_down = True
            return {"nudged": "down"}
        except Exception as e:
            self.log_message("Error nudging down: " + str(e))
            raise

    def _set_signature(self, numerator, denominator):
        """Set time signature"""
        try:
            self._song.signature_numerator = int(numerator)
            self._song.signature_denominator = int(denominator)
            return {
                "signature_numerator": int(numerator),
                "signature_denominator": int(denominator),
            }
        except Exception as e:
            self.log_message("Error setting signature: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Crossfader
    # ═══════════════════════════════════════════════════════════════

    def _get_crossfader(self):
        """Get master crossfader position"""
        try:
            value = self._song.master_track.mixer_device.crossfader.value
            return {"crossfader": value}
        except Exception as e:
            self.log_message("Error getting crossfader: " + str(e))
            raise

    def _set_crossfader(self, value):
        """Set master crossfader position (0.0–1.0)"""
        try:
            self._song.master_track.mixer_device.crossfader.value = float(value)
            return {"crossfader": float(value)}
        except Exception as e:
            self.log_message("Error setting crossfader: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Groove
    # ═══════════════════════════════════════════════════════════════

    def _get_groove_amount(self):
        """Get global groove amount"""
        try:
            return {"groove_amount": self._song.groove_amount}
        except Exception as e:
            self.log_message("Error getting groove amount: " + str(e))
            raise

    def _set_groove_amount(self, amount):
        """Set global groove amount (0.0–1.0)"""
        try:
            self._song.groove_amount = float(amount)
            return {"groove_amount": float(amount)}
        except Exception as e:
            self.log_message("Error setting groove amount: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # System / Monitoring
    # ═══════════════════════════════════════════════════════════════

    def _get_cpu_load(self):
        """Get CPU usage: average and peak"""
        try:
            app = self.application()
            return {
                "average_percent": app.average_process_usage,
                "peak_percent": app.peak_process_usage,
            }
        except Exception as e:
            self.log_message("Error getting CPU load: " + str(e))
            raise

    def _get_live_version(self):
        """Get Live version info"""
        try:
            app = self.application()
            return {
                "version_string": app.get_version_string(),
                "major": app.get_major_version(),
                "minor": app.get_minor_version(),
                "bugfix": app.get_bugfix_version(),
                "build_id": app.get_build_id(),
            }
        except Exception as e:
            self.log_message("Error getting Live version: " + str(e))
            raise

    def _get_tempo_follower(self):
        """Get whether tempo follower is enabled"""
        try:
            return {"enabled": self._song.tempo_follower_enabled}
        except Exception as e:
            self.log_message("Error getting tempo follower: " + str(e))
            raise

    def _set_tempo_follower(self, enabled):
        """Enable/disable tempo follower"""
        try:
            self._song.tempo_follower_enabled = bool(enabled)
            return {"enabled": bool(enabled)}
        except Exception as e:
            self.log_message("Error setting tempo follower: " + str(e))
            raise

    def _get_control_surfaces(self):
        """List active control surfaces"""
        try:
            app = self.application()
            cs_list = app.control_surfaces
            result = []
            for i, cs in enumerate(cs_list):
                result.append({"slot": i, "active": cs is not None})
            return {"control_surfaces": result, "count": len(result)}
        except Exception as e:
            self.log_message("Error getting control surfaces: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Track routing
    # ═══════════════════════════════════════════════════════════════

    def _get_track_routing(self, track_index):
        """Get input/output routing for a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            return {
                "input_routing": track.current_input_routing,
                "input_sub_routing": track.current_input_sub_routing,
                "available_input_types": [
                    rt.display_name for rt in track.available_input_routing_types
                ],
                "available_input_channels": [
                    rc.display_name for rc in track.available_input_routing_channels
                ],
                "output_routing": track.current_output_routing,
                "output_sub_routing": track.current_output_sub_routing,
                "available_output_types": [
                    rt.display_name for rt in track.available_output_routing_types
                ],
                "available_output_channels": [
                    rc.display_name for rc in track.available_output_routing_channels
                ],
            }
        except Exception as e:
            self.log_message("Error getting track routing: " + str(e))
            raise

    def _set_track_input_routing(self, track_index, routing_type, channel=None):
        """Set input routing for a track by type name"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            # Find matching routing type
            for rt in track.available_input_routing_types:
                if rt.display_name == routing_type:
                    track.input_routing_type = rt
                    break
            else:
                raise Exception("Input routing type not found: " + routing_type)
            if channel is not None:
                for rc in track.available_input_routing_channels:
                    if rc.display_name == channel:
                        track.input_routing_channel = rc
                        break
            return {
                "input_routing": track.current_input_routing,
                "input_sub_routing": track.current_input_sub_routing,
            }
        except Exception as e:
            self.log_message("Error setting input routing: " + str(e))
            raise

    def _set_track_output_routing(self, track_index, routing_type, channel=None):
        """Set output routing for a track by type name"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            for rt in track.available_output_routing_types:
                if rt.display_name == routing_type:
                    track.output_routing_type = rt
                    break
            else:
                raise Exception("Output routing type not found: " + routing_type)
            if channel is not None:
                for rc in track.available_output_routing_channels:
                    if rc.display_name == channel:
                        track.output_routing_channel = rc
                        break
            return {
                "output_routing": track.current_output_routing,
                "output_sub_routing": track.current_output_sub_routing,
            }
        except Exception as e:
            self.log_message("Error setting output routing: " + str(e))
            raise

    def _set_track_solo(self, track_index, solo):
        """Set a track's solo state."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            self._song.tracks[track_index].solo = bool(solo)
            return {"track_index": track_index, "solo": bool(solo)}
        except Exception as e:
            self.log_message("Error setting track solo: " + str(e))
            raise

    def _set_track_mute(self, track_index, mute):
        """Set a track's mute state."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            self._song.tracks[track_index].mute = bool(mute)
            return {"track_index": track_index, "mute": bool(mute)}
        except Exception as e:
            self.log_message("Error setting track mute: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Master track
    # ═══════════════════════════════════════════════════════════════

    def _get_master_track(self):
        """Get master track info: volume, pan, devices"""
        try:
            master = self._song.master_track
            devices = []
            for device_index, device in enumerate(master.devices):
                devices.append(
                    {
                        "index": device_index,
                        "name": device.name,
                        "class_name": device.class_name,
                        "type": self._get_device_type(device),
                    }
                )
            return {
                "volume": master.mixer_device.volume.value,
                "panning": master.mixer_device.panning.value,
                "devices": devices,
            }
        except Exception as e:
            self.log_message("Error getting master track: " + str(e))
            raise

    def _get_master_device_parameters(self, device_index):
        """Read all parameters of a device on the master track"""
        try:
            master = self._song.master_track
            if device_index < 0 or device_index >= len(master.devices):
                raise IndexError("Master device index out of range")
            device = master.devices[device_index]
            parameters = []
            for param in device.parameters:
                p = {
                    "name": param.name,
                    "value": param.value,
                    "min": param.min,
                    "max": param.max,
                    "is_quantized": param.is_quantized,
                }
                if param.is_quantized and hasattr(param, "value_items"):
                    try:
                        p["value_items"] = list(param.value_items)
                    except Exception:
                        p["value_items"] = None
                else:
                    p["value_items"] = None
                parameters.append(p)
            return {
                "device_name": device.name,
                "device_class": device.class_name,
                "parameters": parameters,
            }
        except Exception as e:
            self.log_message("Error getting master device parameters: " + str(e))
            raise

    def _set_master_device_parameter(self, device_index, parameter_name, value):
        """Set a device parameter value on the master track"""
        try:
            master = self._song.master_track
            if device_index < 0 or device_index >= len(master.devices):
                raise IndexError("Master device index out of range")
            device = master.devices[device_index]
            for param in device.parameters:
                if (
                    param.name == parameter_name
                    and hasattr(param, "value")
                    and not getattr(param, "is_enabled", False) == False
                ):
                    if param.is_quantized:
                        param.value = int(round(value))
                    else:
                        param.value = float(value)
                    return {"name": param.name, "value": param.value}
            raise ValueError(
                "Parameter '{0}' not found or is read-only".format(parameter_name)
            )
        except Exception as e:
            self.log_message("Error setting master device parameter: " + str(e))
            raise

    def _load_browser_item_on_master(self, item_uri):
        """Load a browser item onto the master track by its URI"""
        try:
            master = self._song.master_track
            app = self.application()
            item = self._find_browser_item_by_uri(app.browser, item_uri)
            if not item:
                raise ValueError(
                    "Browser item with URI '{0}' not found".format(item_uri)
                )
            self._song.view.selected_track = master
            app.browser.load_item(item)
            return {
                "loaded": True,
                "item_name": item.name,
                "uri": item_uri,
            }
        except Exception as e:
            self.log_message("Error loading browser item on master: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _set_master_volume(self, value):
        """Set master volume (0.0–1.0)"""
        try:
            self._song.master_track.mixer_device.volume.value = float(value)
            return {"volume": float(value)}
        except Exception as e:
            self.log_message("Error setting master volume: " + str(e))
            raise

    def _set_master_panning(self, value):
        """Set master panning (-1.0–1.0)"""
        try:
            self._song.master_track.mixer_device.panning.value = float(value)
            return {"panning": float(value)}
        except Exception as e:
            self.log_message("Error setting master panning: " + str(e))
            raise

    def _set_track_volume(self, track_index, value):
        """Set a track's volume (0.0–1.0)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            track.mixer_device.volume.value = float(value)
            return {"track_index": track_index, "volume": float(value)}
        except Exception as e:
            self.log_message("Error setting track volume: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Clip Envelopes (Modulation)
    # ═══════════════════════════════════════════════════════════════

    def _resolve_envelope_target(self, track, target):
        """Resolve a target string to a DeviceParameter for modulation envelopes.

        Supported targets:
          "volume"              → track.mixer_device.volume
          "panning"             → track.mixer_device.panning
          "send_N"              → track.mixer_device.sends[N]
          "device_N_PARAMNAME"  → device[N].parameters[PARAMNAME]
        """
        if target == "volume":
            return track.mixer_device.volume
        elif target == "panning":
            return track.mixer_device.panning
        elif target.startswith("send_"):
            parts = target.split("_")
            if len(parts) >= 2:
                idx = int(parts[1])
                if idx < len(track.mixer_device.sends):
                    return track.mixer_device.sends[idx]
                raise IndexError(f"Send index {idx} out of range")
        elif target.startswith("device_"):
            # Format: device_INDEX_PARAMNAME
            parts = target.split("_", 2)
            if len(parts) >= 3:
                dev_idx = int(parts[1])
                param_name = parts[2]
                if dev_idx < len(track.devices):
                    device = track.devices[dev_idx]
                    for param in device.parameters:
                        if param.name == param_name:
                            return param
                    raise ValueError(
                        f"Parameter '{param_name}' not found on device {dev_idx}"
                    )
                raise IndexError(f"Device index {dev_idx} out of range")
        raise ValueError(f"Unknown envelope target: {target}")

    def _debug_clip_envelopes(self, track_index, clip_index, is_arrangement=True):
        """Exhaustive diagnostic of a clip: all properties + all envelope data."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]

            if is_arrangement:
                clips = list(track.arrangement_clips)
                if clip_index < 0 or clip_index >= len(clips):
                    raise IndexError("Arrangement clip index out of range")
                clip = clips[clip_index]
                clip_type = "arrangement"
            else:
                if clip_index < 0 or clip_index >= len(track.clip_slots):
                    raise IndexError("Session clip slot index out of range")
                slot = track.clip_slots[clip_index]
                if not slot.has_clip:
                    return {"clip_type": "session", "has_clip": False}
                clip = slot.clip
                clip_type = "session"

            info = {
                "clip_type": clip_type,
                "name": clip.name,
                "is_midi_clip": clip.is_midi_clip,
                "is_audio_clip": clip.is_audio_clip,
                "length": clip.length,
                "start_time": getattr(clip, "start_time", None),
                "color": clip.color,
                "is_playing": clip.is_playing,
                "has_envelopes": False,
                "automation_envelopes": [],
            }

            # Check has_envelopes
            try:
                info["has_envelopes"] = clip.has_envelopes
            except Exception as e:
                info["has_envelopes_error"] = str(e)

            # Try automation_envelopes (plural) – list all envelopes
            try:
                env_list = clip.automation_envelopes
                self.log_message(f"DEBUG automation_envelopes type: {type(env_list)}")
                for env in env_list:
                    env_info = {"points": []}
                    try:
                        env_info["parameter_name"] = env.parameter.name
                    except Exception:
                        env_info["parameter_name"] = "?"
                    try:
                        for p in env.points:
                            env_info["points"].append(
                                {
                                    "time": float(p[0]),
                                    "value": float(p[1]),
                                }
                            )
                    except Exception as pt_err:
                        env_info["points_error"] = str(pt_err)
                    info["automation_envelopes"].append(env_info)
            except Exception as e:
                info["automation_envelopes_error"] = str(e)

            # Also try known targets directly
            known_targets = ["volume", "panning"]
            for dev_idx, dev in enumerate(track.devices):
                for p in dev.parameters:
                    tgt = f"device_{dev_idx}_{p.name}"
                    known_targets.append(tgt)

            envelope_by_target = {}
            for target_name in known_targets:
                try:
                    param = self._resolve_envelope_target(track, target_name)
                    env = clip.automation_envelope(param)
                    if env is not None:
                        pts = []
                        for p in env.points:
                            pts.append({"time": float(p[0]), "value": float(p[1])})
                        if pts:
                            envelope_by_target[target_name] = {
                                "param_name": param.name,
                                "points": pts,
                            }
                except Exception as e:
                    envelope_by_target[target_name] = {"error": str(e)}

            info["envelope_by_target"] = envelope_by_target

            return info
        except Exception as e:
            self.log_message("Error in debug_clip_envelopes: " + str(e))
            raise

    def _get_clip_envelope(self, track_index, clip_index, target, is_arrangement=True):
        """Read envelope points from a clip's modulation envelope.

        Returns all clip envelope info for diagnostics.
        """
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]

            if is_arrangement:
                clips = list(track.arrangement_clips)
                if clip_index < 0 or clip_index >= len(clips):
                    raise IndexError("Arrangement clip index out of range")
                clip = clips[clip_index]
            else:
                if clip_index < 0 or clip_index >= len(track.clip_slots):
                    raise IndexError("Session clip slot index out of range")
                slot = track.clip_slots[clip_index]
                if not slot.has_clip:
                    return {"has_clip": False}
                clip = slot.clip

            param = self._resolve_envelope_target(track, target)

            # ── Clip properties ────────────────────────────────────────────
            info = {
                "target": target,
                "clip_type": "arrangement" if is_arrangement else "session",
                "name": clip.name,
                "is_midi": clip.is_midi_clip,
                "is_audio": clip.is_audio_clip,
                "length": clip.length,
            }

            # ── has_envelopes ──────────────────────────────────────────────
            try:
                info["has_envelopes"] = clip.has_envelopes
            except Exception:
                try:
                    info["has_envelopes"] = clip.has_envelopes()
                except Exception as e2:
                    info["has_envelopes"] = str(e2)

            # ── automation_envelopes (plural): list all ────────────────────
            env_list = []
            try:
                raw = clip.automation_envelopes
                if raw is not None:
                    for env in raw:
                        entry = {"points": []}
                        try:
                            entry["parameter_name"] = env.parameter.name
                        except Exception:
                            entry["parameter_name"] = "?"
                        try:
                            for p in env.points:
                                entry["points"].append(
                                    {
                                        "time": float(p[0]),
                                        "value": float(p[1]),
                                    }
                                )
                        except Exception as pt_err:
                            entry["points_error"] = str(pt_err)
                        env_list.append(entry)
                info["automation_envelopes"] = env_list
            except Exception:
                try:
                    raw = clip.automation_envelopes()
                    if raw is not None:
                        for env in raw:
                            entry = {"points": []}
                            try:
                                entry["parameter_name"] = env.parameter.name
                            except Exception:
                                entry["parameter_name"] = "?"
                            try:
                                for p in env.points:
                                    entry["points"].append(
                                        {
                                            "time": float(p[0]),
                                            "value": float(p[1]),
                                        }
                                    )
                            except Exception as pt_err:
                                entry["points_error"] = str(pt_err)
                            env_list.append(entry)
                    info["automation_envelopes"] = env_list
                except Exception as e2:
                    info["automation_envelopes_error"] = str(e2)

            # ── automation_envelope(singular) for target param ────────────
            try:
                env = clip.automation_envelope(param)
                if env is not None:
                    pts = []
                    clip_start = getattr(clip, "start_time", 0.0)
                    clip_end = getattr(clip, "end_time", clip_start + 4.0)
                    for ev in env.events_in_range(clip_start, clip_end):
                        pts.append({"time": ev.time, "value": ev.value})
                    info["target_envelope_points"] = pts
                else:
                    info["target_envelope_points"] = []
                    info["target_envelope_note"] = "automation_envelope returned None"
            except Exception as e:
                info["target_envelope_error"] = str(e)

            return info
        except Exception as e:
            self.log_message("Error getting clip envelope: " + str(e))
            raise

    def _set_clip_envelope(
        self, track_index, clip_index, target, points, is_arrangement=True
    ):
        """Set modulation envelope points on an arrangement clip."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            param = self._resolve_envelope_target(track, target)
            clips = list(track.arrangement_clips)
            if clip_index < 0 or clip_index >= len(clips):
                raise IndexError("Arrangement clip index out of range")
            clip = clips[clip_index]
            # Remove existing envelope if any
            clip.clear_envelope(param)
            if not points:
                return {"point_count": 0}
            # Create fresh envelope
            env = clip.create_automation_envelope(param)
            for p in points:
                t = float(p["time"])
                v = float(p["value"])
                d = float(p.get("duration", 0.0))
                env.insert_step(t, v, d)
            return {"point_count": len(points)}
        except Exception as e:
            self.log_message("Error setting clip envelope: " + str(e))
            raise

    def _get_track_automation(self, track_index, target):
        """Read track-level automation envelope (arrangement automation lanes)."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            param = self._resolve_envelope_target(track, target)

            song_start = getattr(self._song, "start_time", 0.0)
            song_end = getattr(self._song, "song_length", 232.0)

            info = {
                "track_name": track.name,
                "target": target,
                "parameter": param.name,
            }

            env = None
            try:
                env = track.automation_envelope(param)
            except Exception:
                pass

            if env is not None:
                info["has_automation"] = True
                pts = []
                try:
                    for ev in env.events_in_range(song_start, song_end):
                        pts.append({"time": ev.time, "value": ev.value})
                except Exception:
                    try:
                        for p in env.points:
                            pts.append({"time": float(p[0]), "value": float(p[1])})
                    except Exception:
                        pass
                info["events"] = pts
                info["event_count"] = len(pts)
            else:
                info["has_automation"] = False
                info["note"] = "track.automation_envelope returned None"

            return info
        except Exception as e:
            self.log_message("Error getting track automation: " + str(e))
            raise

    def _set_automation_curve(
        self, track_index, clip_index, target, points, is_arrangement=True
    ):
        """Set automation curve from a list of points using connected steps.

        Each point: {'time': float (beats), 'value': float (raw 0-127)}.
        Uses insert_step() with connected durations to create proper step automation.
        """
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            param = self._resolve_envelope_target(track, target)

            if is_arrangement:
                clips = list(track.arrangement_clips)
                if clip_index < 0 or clip_index >= len(clips):
                    raise IndexError("Arrangement clip index out of range")
                clip = clips[clip_index]
            else:
                if clip_index < 0 or clip_index >= len(track.clip_slots):
                    raise IndexError("Session clip slot index out of range")
                slot = track.clip_slots[clip_index]
                if not slot.has_clip:
                    raise ValueError("No clip in slot")
                clip = slot.clip

            is_audio = hasattr(clip, "is_audio_clip") and clip.is_audio_clip
            is_midi = hasattr(clip, "is_midi_clip") and clip.is_midi_clip

            if is_arrangement and is_midi:
                # MIDI arrangement clips: use temp session clip workaround
                clip_start = getattr(clip, "start_time", 0.0)
                clip_end = getattr(clip, "end_time", clip_start + 4.0)
                orig_length = clip.length if hasattr(clip, "length") else 4.0
                live_notes = tuple(clip.get_notes(0.0, 0, orig_length, 127))

                temp_slot = None
                for i in range(len(track.clip_slots)):
                    if not track.clip_slots[i].has_clip:
                        temp_slot = track.clip_slots[i]
                        break
                if temp_slot is None:
                    raise Exception("No empty session clip slot available")

                temp_slot.create_clip(orig_length)
                if live_notes:
                    temp_slot.clip.set_notes(live_notes)

                env = temp_slot.clip.create_automation_envelope(param)
                self._apply_curve(env, points, 0.0, orig_length)
                track.delete_clip(clip)
                track.duplicate_clip_to_arrangement(temp_slot.clip, float(clip_start))
                temp_slot.delete_clip()
            else:
                # Session clips or audio arrangement clips: direct approach
                env = None
                try:
                    env = clip.automation_envelope(param)
                except Exception:
                    pass
                if env is None:
                    env = clip.create_automation_envelope(param)

                clip_start = getattr(clip, "start_time", 0.0)
                clip_end = getattr(clip, "end_time", clip_start + 4.0)
                env.delete_events_in_range(clip_start, clip_end)
                self._apply_curve(env, points, 0.0, clip_end)

            return {
                "action": "set_automation_curve",
                "parameter": param.name,
                "points_count": len(points),
                "done": True,
            }
        except Exception as e:
            self.log_message("Error setting automation curve: " + str(e))
            raise

    def _apply_curve(self, env, points, clip_start, clip_end):
        """Apply a list of automated points to an envelope using connected steps."""
        if not points:
            return
        sorted_points = sorted(points, key=lambda p: p["time"])
        for i in range(len(sorted_points)):
            t = sorted_points[i]["time"]
            v = sorted_points[i]["value"]
            if i < len(sorted_points) - 1:
                dur = sorted_points[i + 1]["time"] - t
                if dur <= 0:
                    dur = 0.001
            else:
                dur = max(clip_end - t, 0.1)
            env.insert_step(t, dur, v)

    def _set_arrangement_clip_envelope(self, track_index, clip_index, target, points):
        """Set modulation envelope on an arrangement clip.

        For MIDI clips: uses a temp session clip workaround (duplicate → envelope → delete).
        For audio clips: applies envelope directly on the arrangement clip."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            param = self._resolve_envelope_target(track, target)
            clips = list(track.arrangement_clips)
            if clip_index < 0 or clip_index >= len(clips):
                raise IndexError("Arrangement clip index out of range")
            src_clip = clips[clip_index]

            if not points:
                return {"point_count": 0}

            # Check if it's an audio clip
            is_audio = hasattr(src_clip, "is_audio_clip") and src_clip.is_audio_clip

            if is_audio:
                # Audio arrangement clips support create_automation_envelope directly
                env = src_clip.create_automation_envelope(param)
                for p in points:
                    t = float(p["time"])
                    v = float(p["value"])
                    d = float(p.get("duration", 0.0))
                    env.insert_step(t, v, d)
                return {"point_count": len(points), "method": "direct_audio"}
            else:
                # MIDI clip workaround: temp session clip → envelope → duplicate back
                length = src_clip.length
                start_time = src_clip.start_time
                live_notes = tuple(src_clip.get_notes(0.0, 0, length, 127))

                temp_slot = None
                for i in range(len(track.clip_slots)):
                    if not track.clip_slots[i].has_clip:
                        temp_slot = track.clip_slots[i]
                        break
                if temp_slot is None:
                    raise Exception("No empty session clip slot available")

                temp_slot.create_clip(length)
                if live_notes:
                    temp_slot.clip.set_notes(live_notes)

                env = temp_slot.clip.create_automation_envelope(param)
                for p in points:
                    t = float(p["time"])
                    v = float(p["value"])
                    d = float(p.get("duration", 0.0))
                    env.insert_step(t, v, d)

                track.delete_clip(src_clip)
                track.duplicate_clip_to_arrangement(temp_slot.clip, float(start_time))
                temp_slot.delete_clip()

                return {
                    "point_count": len(points),
                    "start_time": start_time,
                    "length": length,
                    "method": "temp_midi",
                }
        except Exception as e:
            self.log_message("Error setting arrangement clip envelope: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Extended Device Management
    # ═══════════════════════════════════════════════════════════════

    def _get_track_and_device(
        self, track_index, device_index, device_name="", chain_index=0
    ):
        """Resolve a track and device, optionally in a chain."""
        if track_index < 0 or track_index >= len(self._song.tracks):
            raise IndexError("Track index out of range")
        track = self._song.tracks[track_index]
        if device_name:
            for i, d in enumerate(track.devices):
                if d.name == device_name:
                    device_index = i
                    break
            else:
                raise ValueError("Device not found: " + device_name)
        if device_index < 0 or device_index >= len(track.devices):
            raise IndexError("Device index out of range")
        device = track.devices[device_index]
        if chain_index > 0 and hasattr(device, "chains") and device.chains:
            if chain_index - 1 < len(device.chains):
                chain = device.chains[chain_index - 1]
                return chain, chain.devices[0] if chain.devices else None
        return track, device

    def _enable_device(self, track_index, device_index, device_name="", chain_index=0):
        """Enable a device on a track."""
        try:
            _, device = self._get_track_and_device(
                track_index, device_index, device_name, chain_index
            )
            device.is_enabled = True
            return {"enabled": True, "device_name": device.name}
        except Exception as e:
            self.log_message("Error enabling device: " + str(e))
            raise

    def _disable_device(self, track_index, device_index, device_name="", chain_index=0):
        """Disable (bypass) a device on a track."""
        try:
            _, device = self._get_track_and_device(
                track_index, device_index, device_name, chain_index
            )
            device.is_enabled = False
            return {"enabled": False, "device_name": device.name}
        except Exception as e:
            self.log_message("Error disabling device: " + str(e))
            raise

    def _navigate_device_preset(
        self, track_index, device_index, chain_index, direction
    ):
        """Navigate device presets."""
        try:
            _, device = self._get_track_and_device(
                track_index, device_index, "", chain_index
            )
            if direction == "next":
                device.presets.next()
            elif direction == "previous":
                device.presets.previous()
            return {"direction": direction, "device_name": device.name}
        except Exception as e:
            self.log_message("Error navigating device preset: " + str(e))
            raise

    def _get_chain_info(self, track_index, device_index, chain_index):
        """List chains in a rack device, or devices within a specific chain."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]
            result = {"device_name": device.name, "device_class": device.class_name}
            if hasattr(device, "chains") and device.chains:
                if chain_index > 0:
                    if chain_index - 1 < len(device.chains):
                        chain = device.chains[chain_index - 1]
                        devices = []
                        for d in chain.devices:
                            devices.append(
                                {
                                    "name": d.name,
                                    "class_name": d.class_name,
                                    "is_enabled": d.is_enabled,
                                }
                            )
                        result["chain_devices"] = devices
                    else:
                        raise IndexError("Chain index out of range")
                else:
                    chains = []
                    for i, c in enumerate(device.chains):
                        chains.append(
                            {
                                "index": i + 1,
                                "name": c.name if c.name else "Chain " + str(i + 1),
                                "device_count": len(c.devices),
                            }
                        )
                    result["chains"] = chains
            else:
                result["chains"] = []
            return result
        except Exception as e:
            self.log_message("Error getting chain info: " + str(e))
            raise

    def _get_drum_pad_info(self, track_index, device_index):
        """List filled drum pads in a Drum Rack."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]
            pads = []
            if hasattr(device, "drum_pads"):
                for pad in device.drum_pads:
                    if pad.chains and len(pad.chains) > 0:
                        chain = pad.chains[0]
                        pads.append(
                            {
                                "note": pad.note,
                                "name": chain.name
                                if chain.name
                                else "Pad " + str(pad.note),
                                "device_count": len(chain.devices),
                            }
                        )
            return {"pads": pads}
        except Exception as e:
            self.log_message("Error getting drum pad info: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Track Mixer Extras
    # ═══════════════════════════════════════════════════════════════

    def _set_track_panning(self, track_index, panning):
        """Set a track's panning (-1.0 to 1.0)."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            track.mixer_device.panning.value = float(panning)
            return {"track_index": track_index, "panning": float(panning)}
        except Exception as e:
            self.log_message("Error setting track panning: " + str(e))
            raise

    def _get_track_volume(self, track_index):
        """Get a track's volume and panning info."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            vol = track.mixer_device.volume
            pan = track.mixer_device.panning
            return {
                "volume": vol.value,
                "volume_min": vol.min,
                "volume_max": vol.max,
                "panning": pan.value,
            }
        except Exception as e:
            self.log_message("Error getting track volume: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # View Control
    # ═══════════════════════════════════════════════════════════════

    def _set_ableton_view(self, view):
        """Switch Ableton's main view."""
        try:
            if view == "Arranger":
                self._song.view.show_view("Arranger")
            elif view == "Session":
                self._song.view.show_view("Session")
            elif view == "Detail":
                self._song.view.show_view("Detail")
            elif view == "Detail/Clip":
                self._song.view.show_view("Detail/Clip")
            elif view == "Detail/DeviceChain":
                self._song.view.show_view("Detail/DeviceChain")
            elif view == "Browser":
                self._song.view.show_view("Browser")
            return {"view": view}
        except Exception as e:
            self.log_message("Error setting view: " + str(e))
            raise

    def _control_arrangement_view(self, action, track_index):
        """Control the arrangement view."""
        try:
            if action == "zoom_in":
                self._song.view.zoom_in()
            elif action == "zoom_out":
                self._song.view.zoom_out()
            elif action == "scroll_left":
                self._song.view.scroll_left()
            elif action == "scroll_right":
                self._song.view.scroll_right()
            elif action == "follow_on":
                self._song.view.follow_song = True
            elif action == "follow_off":
                self._song.view.follow_song = False
            elif action == "collapse_track":
                if track_index >= 0 and track_index < len(self._song.tracks):
                    self._song.tracks[track_index].view.is_collapsed = True
            elif action == "expand_track":
                if track_index >= 0 and track_index < len(self._song.tracks):
                    self._song.tracks[track_index].view.is_collapsed = False
            return {"action": action}
        except Exception as e:
            self.log_message("Error controlling arrangement view: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Cue Points
    # ═══════════════════════════════════════════════════════════════

    def _get_cue_points(self):
        """List all cue points with bar positions."""
        try:
            cues = []
            for c in self._song.cue_points:
                cues.append(
                    {
                        "name": c.name,
                        "time": c.time,
                        "bar": c.time
                        / self._song.signature_numerator
                        * 4.0
                        / (self._song.signature_denominator / 4.0)
                        if self._song.signature_denominator
                        else 0,
                    }
                )
            return {"cue_points": cues}
        except Exception as e:
            self.log_message("Error getting cue points: " + str(e))
            raise

    def _create_cue_point(self, bar, beat, name):
        """Create a cue point at position."""
        try:
            from math import floor

            beat_time = (
                (bar - 1)
                * float(self._song.signature_numerator)
                * (4.0 / float(self._song.signature_denominator))
                + beat
                if bar > 0
                else beat
            )
            self._song.create_cue(beat_time)
            cue = self._song.cue_points[-1]
            if name:
                cue.name = str(name)
            return {"name": cue.name, "time": beat_time}
        except Exception as e:
            self.log_message("Error creating cue point: " + str(e))
            raise

    def _delete_cue_point(self, bar, beat):
        """Delete a cue point at a position."""
        try:
            cue_to_delete = None
            for c in self._song.cue_points:
                c_bar = (
                    c.time
                    / self._song.signature_numerator
                    * 4.0
                    / (self._song.signature_denominator / 4.0)
                    if self._song.signature_denominator
                    else 0
                )
                if bar > 0 and int(c_bar) == bar:
                    cue_to_delete = c
                    break
                elif abs(c.time - beat) < 0.01:
                    cue_to_delete = c
                    break
            if cue_to_delete:
                self._song.delete_cue(cue_to_delete)
                return {"deleted": True}
            return {"deleted": False}
        except Exception as e:
            self.log_message("Error deleting cue point: " + str(e))
            raise

    def _jump_to_cue_point(self, direction, name):
        """Jump to next/prev cue point or by name."""
        try:
            if name:
                for c in self._song.cue_points:
                    if c.name == name:
                        self._song.current_song_time = c.time
                        return {"jumped_to": name, "time": c.time}
                raise ValueError("Cue point not found: " + name)
            if direction == "next":
                self._song.jump_to_next_cue()
            elif direction == "prev":
                self._song.jump_to_prev_cue()
            return {"direction": direction}
        except Exception as e:
            self.log_message("Error jumping to cue point: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Arrangement
    # ═══════════════════════════════════════════════════════════════

    def _set_arrangement_loop(
        self, enabled, start_bar, end_bar, start_beat, length_beats
    ):
        """Enable/disable arrangement loop and set the region."""
        try:
            self._song.loop = bool(enabled)
            if start_bar > 0:
                beat_start = (start_bar - 1) * self._song.signature_numerator
            else:
                beat_start = start_beat
            self._song.loop_start = float(beat_start)
            if end_bar > 0:
                beat_len = (end_bar - start_bar) * self._song.signature_numerator
            elif length_beats > 0:
                beat_len = length_beats
            else:
                beat_len = self._song.signature_numerator * 4
            self._song.loop_length = float(beat_len)
            return {
                "enabled": bool(enabled),
                "start": float(beat_start),
                "length": float(beat_len),
            }
        except Exception as e:
            self.log_message("Error setting arrangement loop: " + str(e))
            raise

    def _create_arrangement_midi_clip(
        self, track_index, start_bar, end_bar, start_beat, length_beats, name
    ):
        """Create an empty MIDI clip in the arrangement."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if start_bar > 0:
                start_time = (start_bar - 1) * self._song.signature_numerator
            else:
                start_time = start_beat
            if end_bar > 0:
                length = (end_bar - start_bar) * self._song.signature_numerator
            else:
                length = length_beats
            clip = track.create_clip(start_time, length)
            if name:
                clip.name = str(name)
            return {
                "track_index": track_index,
                "start_time": start_time,
                "length": length,
                "name": clip.name,
            }
        except Exception as e:
            self.log_message("Error creating arrangement clip: " + str(e))
            raise

    def _create_arrangement_audio_clip(
        self, track_index, file_path, start_bar, start_beat
    ):
        """Place an audio file as a clip in the arrangement."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if start_bar > 0:
                start_time = (start_bar - 1) * self._song.signature_numerator
            else:
                start_time = start_beat
            try:
                from ableton.v2.audio_file import AudioFile

                audio_file = AudioFile(path=file_path.encode("utf-8"))
                clip = track.create_clip(start_time, audio_file.length)
                clip.set_audio_file(audio_file)
                return {
                    "track_index": track_index,
                    "start_time": start_time,
                    "file_path": file_path,
                }
            except ImportError:
                clip = track.create_clip(start_time, 4.0)
                return {
                    "track_index": track_index,
                    "start_time": start_time,
                    "warning": "AudioFile not available, created empty clip",
                }
        except Exception as e:
            self.log_message("Error creating arrangement audio clip: " + str(e))
            raise

    def _duplicate_clip_to_arrangement(
        self, track_index, clip_index, destination_bar, destination_beat
    ):
        """Copy a session clip to the arrangement."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip slot index out of range")
            if not track.clip_slots[clip_index].has_clip:
                raise ValueError("No clip in this slot")
            if destination_bar > 0:
                dest_time = (destination_bar - 1) * self._song.signature_numerator
            else:
                dest_time = destination_beat
            track.duplicate_clip_to_arrangement(
                track.clip_slots[clip_index].clip, float(dest_time)
            )
            return {
                "track_index": track_index,
                "clip_index": clip_index,
                "destination_time": dest_time,
            }
        except Exception as e:
            self.log_message("Error duplicating clip to arrangement: " + str(e))
            raise

    # ═══════════════════════════════════════════════════════════════
    # Automation Management
    # ═══════════════════════════════════════════════════════════════

    def _manage_clip_automation(
        self, track_index, clip_index, clip_name, action, parameter_name
    ):
        """Create or clear automation envelopes on arrangement clips."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            clips = list(track.arrangement_clips)
            if clip_name:
                clip = None
                for c in clips:
                    if c.name == clip_name:
                        clip = c
                        break
                if not clip:
                    raise ValueError("Clip not found: " + clip_name)
            else:
                if clip_index < 1 or clip_index > len(clips):
                    raise IndexError("Clip index out of range")
                clip = clips[clip_index - 1]
            param = self._resolve_envelope_target(track, parameter_name)
            if action == "create":
                env = clip.create_automation_envelope(param)
                return {"created": True, "parameter": parameter_name}
            elif action == "clear":
                clip.clear_envelope(param)
                return {"cleared": True, "parameter": parameter_name}
            elif action == "clear_all":
                for p in [track.mixer_device.volume, track.mixer_device.panning]:
                    try:
                        clip.clear_envelope(p)
                    except Exception:
                        pass
                return {"cleared_all": True}
            return {"action": action}
        except Exception as e:
            self.log_message("Error managing clip automation: " + str(e))
            raise

    def _add_clip_envelope_point(
        self, track_index, clip_index, target, time, value, duration, is_arrangement
    ):
        """Write an automation point or step into a clip's envelope."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if is_arrangement:
                clips = list(track.arrangement_clips)
                if clip_index < 0 or clip_index >= len(clips):
                    raise IndexError("Clip index out of range")
                clip = clips[clip_index]
            else:
                if clip_index < 0 or clip_index >= len(track.clip_slots):
                    raise IndexError("Clip slot index out of range")
                if not track.clip_slots[clip_index].has_clip:
                    raise ValueError("No clip in this slot")
                clip = track.clip_slots[clip_index].clip
            param = self._resolve_envelope_target(track, target)
            env = clip.automation_envelope(param)
            if env is None:
                env = clip.create_automation_envelope(param)
            env.insert_step(float(time), float(value), float(duration))
            return {
                "time": time,
                "value": value,
                "duration": duration,
                "target": target,
            }
        except Exception as e:
            self.log_message("Error adding envelope point: " + str(e))
            raise

    def _clear_clip_envelope(self, track_index, clip_index, target, is_arrangement):
        """Clear automation envelope for a parameter on a clip."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if is_arrangement:
                clips = list(track.arrangement_clips)
                if clip_index < 0 or clip_index >= len(clips):
                    raise IndexError("Clip index out of range")
                clip = clips[clip_index]
            else:
                if clip_index < 0 or clip_index >= len(track.clip_slots):
                    raise IndexError("Clip slot index out of range")
                if not track.clip_slots[clip_index].has_clip:
                    raise ValueError("No clip in this slot")
                clip = track.clip_slots[clip_index].clip
            param = self._resolve_envelope_target(track, target)
            clip.clear_envelope(param)
            return {"cleared": True, "target": target}
        except Exception as e:
            self.log_message("Error clearing clip envelope: " + str(e))
            raise

    def _experiment_envelope(self, track_index, clip_index, target, is_arrangement):
        """Run comprehensive envelope experiments."""
        results = {}
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if is_arrangement:
                clips = list(track.arrangement_clips)
                if clip_index < 0 or clip_index >= len(clips):
                    raise IndexError("Clip index out of range")
                clip = clips[clip_index]
                results["clip_type"] = "arrangement"
            else:
                if clip_index < 0 or clip_index >= len(track.clip_slots):
                    raise IndexError("Clip slot index out of range")
                if not track.clip_slots[clip_index].has_clip:
                    raise ValueError("No clip in this slot")
                clip = track.clip_slots[clip_index].clip
                results["clip_type"] = "session"
            param = self._resolve_envelope_target(track, target)
            results["param_name"] = param.name
            results["param_value"] = param.value
            results["clip_name"] = clip.name
            results["clip_length"] = clip.length
            # Test 1: get existing envelope
            env = clip.automation_envelope(param)
            results["existing_envelope"] = env is not None
            if env is None:
                try:
                    env = clip.create_automation_envelope(param)
                    results["created_envelope"] = True
                except Exception as e:
                    results["create_error"] = str(e)
            if env is not None:
                try:
                    env.insert_step(0.0, param.value, 0.0)
                    results["insert_step_point"] = True
                except Exception as e:
                    results["insert_step_point_error"] = str(e)
                try:
                    env.insert_step(1.0, param.value, 1.0)
                    results["insert_step_duration"] = True
                except Exception as e:
                    results["insert_step_duration_error"] = str(e)
                try:
                    events = env.events_in_range(0.0, clip.length)
                    results["events_in_range"] = len(events) if events else 0
                except Exception as e:
                    results["events_in_range_error"] = str(e)
            return results
        except Exception as e:
            self.log_message("Error in envelope experiments: " + str(e))
            return {"error": str(e)}

    def _envelope_dump(self, track_index, clip_index, is_arrangement):
        """Ultra-exhaustive dump of clip envelope state."""
        results = {}
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if is_arrangement:
                clips = list(track.arrangement_clips)
                if clip_index < 0 or clip_index >= len(clips):
                    raise IndexError("Clip index out of range")
                clip = clips[clip_index]
            else:
                if clip_index < 0 or clip_index >= len(track.clip_slots):
                    raise IndexError("Clip slot index out of range")
                if not track.clip_slots[clip_index].has_clip:
                    raise ValueError("No clip in this slot")
                clip = track.clip_slots[clip_index].clip
            results["clip_name"] = clip.name
            results["clip_length"] = clip.length
            results["is_midi_clip"] = getattr(clip, "is_midi_clip", None)
            results["is_audio_clip"] = getattr(clip, "is_audio_clip", None)
            # List all params to check for envelopes
            params_to_check = []
            try:
                for p in track.mixer_device.volume, track.mixer_device.panning:
                    params_to_check.append(("mixer", p.name, p))
                for s in track.mixer_device.sends:
                    params_to_check.append(("send", s.name, s))
                for d_idx, d in enumerate(track.devices):
                    for p in d.parameters:
                        params_to_check.append(("device_%d" % d_idx, p.name, p))
            except Exception as e:
                results["param_enum_error"] = str(e)
            envs_found = []
            for cat, pname, param in params_to_check:
                try:
                    env = clip.automation_envelope(param)
                    if env is not None:
                        envs_found.append(
                            {
                                "category": cat,
                                "parameter": pname,
                                "has_envelope": True,
                            }
                        )
                except Exception:
                    pass
            results["envelopes_found"] = envs_found
            return results
        except Exception as e:
            self.log_message("Error in envelope dump: " + str(e))
            return {"error": str(e)}

    def _test_create_event(self, track_index, clip_index, target, time, value):
        """Test various create_event signatures on the clip envelope."""
        results = {}
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            clips = list(track.arrangement_clips)
            if clip_index < 0 or clip_index >= len(clips):
                raise IndexError("Clip index out of range")
            clip = clips[clip_index]
            param = self._resolve_envelope_target(track, target)
            env = clip.automation_envelope(param)
            if env is None:
                env = clip.create_automation_envelope(param)
            # Try create_event with different signatures
            for args_desc, args in [
                ("(time, value)", (float(time), float(value))),
                ("(time, value, duration)", (float(time), float(value), 0.0)),
            ]:
                try:
                    if len(args) == 2:
                        env.create_event(*args)
                    else:
                        env.create_event(*args)
                    results[args_desc] = "success"
                except Exception as e:
                    results[args_desc] = "error: " + str(e)
            return results
        except Exception as e:
            self.log_message("Error testing create_event: " + str(e))
            return {"error": str(e)}

    # ═══════════════════════════════════════════════════════════════
    # Track Deletion Safety
    # ═══════════════════════════════════════════════════════════════

    def _get_track_deletion_status(self):
        """Check if tracks can be deleted safely."""
        try:
            track_count = len(self._song.tracks)
            return {
                "track_count": track_count,
                "can_delete_any": track_count > 1,
                "min_tracks_remaining": 1,
            }
        except Exception as e:
            self.log_message("Error getting deletion status: " + str(e))
            raise
