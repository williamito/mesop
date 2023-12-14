import os
import sys
import threading

from absl import app, flags

import mesop.protos.ui_pb2 as pb
from mesop.cli.execute_module import execute_module
from mesop.exceptions import format_traceback
from mesop.runtime import enable_debug_mode, reset_runtime, runtime
from mesop.server.flags import port
from mesop.server.server import flask_app
from mesop.server.static_file_serving import configure_static_file_serving
from mesop.utils.runfiles import get_runfile_location

FLAGS = flags.FLAGS

flags.DEFINE_string("path", "", "path to main python module of Mesop app.")
flags.DEFINE_bool("debug", True, "set to true for debug mode.")


def monitor_stdin():
  while True:
    line = sys.stdin.readline().strip()
    if line == "IBAZEL_BUILD_COMPLETED SUCCESS":
      reset_runtime()
      execute_module(get_runfile_location(FLAGS.path))


stdin_thread = threading.Thread(target=monitor_stdin)
stdin_thread.daemon = True
stdin_thread.start()


def main(argv):
  if len(FLAGS.path) < 1:
    raise Exception("Required flag 'path'. Received: " + FLAGS.path)

  if FLAGS.debug:
    enable_debug_mode()

  try:
    execute_module(get_runfile_location(FLAGS.path))
  except Exception as e:
    # Only record error to runtime if in CI mode.
    if FLAGS.debug:
      runtime().add_loading_error(
        pb.ServerError(exception=str(e), traceback=format_traceback())
      )
      print("Exception executing module:", e)
    else:
      raise e

  print("Running with hot reload:")

  configure_static_file_serving(
    flask_app,
    static_file_runfiles_base="mesop/mesop/web/src/app/prod/web_package",
    livereload_script_url=os.environ.get("IBAZEL_LIVERELOAD_URL"),
  )
  flask_app.run(host="0.0.0.0", port=port(), use_reloader=False)


if __name__ == "__main__":
  app.run(main)