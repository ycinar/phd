import run_webrtc_test

netem_thread = run_webrtc_test.jitter_thread('netem_thread')
netem_thread.start()