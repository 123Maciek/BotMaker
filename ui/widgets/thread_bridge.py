"""Thread-safe hand-off from a background thread to the Tk main thread.

Calling widget.after(...) directly from a non-main thread (e.g. a pynput
listener thread, or the update-download thread) is not reliably safe in
Tkinter — it can raise "main thread is not in main loop" depending on timing.
Screens with background threads (macro_recorder, update_progress) should mix
this in and call post_to_ui() from the worker thread instead of self.after().
"""
import queue


class ThreadBridge:
    def init_thread_bridge(self, poll_ms=30):
        self._bridge_queue = queue.Queue()
        self._bridge_poll_ms = poll_ms
        self._bridge_active = True
        self._drain_bridge_queue()

    def post_to_ui(self, callback, *args):
        self._bridge_queue.put((callback, args))

    def stop_thread_bridge(self):
        self._bridge_active = False

    def _drain_bridge_queue(self):
        try:
            while True:
                callback, args = self._bridge_queue.get_nowait()
                callback(*args)
        except queue.Empty:
            pass
        if getattr(self, "_bridge_active", False) and self.winfo_exists():
            self.after(self._bridge_poll_ms, self._drain_bridge_queue)
