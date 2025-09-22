import ctypes
import wave

from time import sleep
from pathlib import Path

from pyaudio import PyAudio


def _alsa_err_handler(filename, line, function, err, fmt):
    pass


ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(
    None,
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_char_p,
)

c_error_handler = ERROR_HANDLER_FUNC(_alsa_err_handler)
asound = ctypes.cdll.LoadLibrary("libasound.so")
asound.snd_lib_error_set_handler(c_error_handler)


class Cycle:
    def __init__(self):
        self.ROUND: int = 0
        self.LAP: int = 0
        self.WORK: int = 25
        self.REST: int = 5
        self.EXTENDED_REST: int = 15
        self.current: None | str = None


class Ring:
    def __init__(self):
        self.BASE = Path("sounds")
        self.WORK_SOUND = self.BASE / "work.wav"
        self.REST_SOUND = self.BASE / "rest.wav"
        self.EXTENDED_REST_SOUND = self.BASE / "extended_rest.wav"

        super().__init__()

    def make_sound(self, wave_path):
        chunk = 1024

        try:
            with wave.open(str(wave_path), "rb") as file:
                audio = PyAudio()
                stream = audio.open(
                    format=audio.get_format_from_width(file.getsampwidth()),
                    channels=file.getnchannels(),
                    rate=file.getframerate(),
                    output=True,
                )
                data = file.readframes(chunk)
                while data:
                    stream.write(data)
                    data = file.readframes(chunk)
                stream.stop_stream()
                stream.close()
                audio.terminate()
        except Exception:
            pass

    def work_sound(self):
        self.make_sound(self.WORK_SOUND)

    def extended_rest_sound(self):
        self.make_sound(self.EXTENDED_REST_SOUND)

    def rest_sound(self):
        self.make_sound(self.REST_SOUND)


class Timer:
    def __init__(self):
        self.cycle = Cycle()
        self.ring = Ring()

    def play_sound(self):
        sound_map = {
            "WORK": self.ring.work_sound,
            "EXTENDED_REST": self.ring.extended_rest_sound,
            "REST": self.ring.rest_sound,
        }

        if self.cycle.current:
            sound = sound_map.get(self.cycle.current)
            if sound:
                sound()

    def display_message(self, timer: None | str = None):
        clock = "00:00" if not timer else timer
        lap = self.cycle.LAP
        rounds = self.cycle.ROUND
        print(
            f"{self.cycle.current} - {clock} - Lap: {lap} - Round: {rounds}", end="\r"
        )

    def countdown(self, minutes: int):
        self.display_message()

        total_seconds = minutes * 60
        while total_seconds > 0:
            minutes, seconds = divmod(total_seconds, 60)
            timer = f"{minutes:02}:{seconds:02}"
            self.display_message(timer)

            sleep(1)
            total_seconds -= 1

        self.display_message()

    def work_countdown(self):
        self.cycle.current = "WORK"
        self.play_sound()
        self.countdown(self.cycle.WORK)

    def extended_rest_countdown(self):
        self.cycle.current = "EXTENDED_REST"
        self.play_sound()
        self.countdown(self.cycle.EXTENDED_REST)

    def rest_countdown(self):
        self.cycle.current = "REST"
        self.play_sound()
        self.countdown(self.cycle.REST)

    def start(self):
        self.work_countdown()

        self.cycle.LAP += 1

        if self.cycle.LAP >= 4:
            self.extended_rest_countdown()
            self.cycle.LAP = 0
            self.cycle.ROUND += 1
        else:
            self.rest_countdown()

        self.start()

    def pause(self):
        pass


if __name__ == "__main__":
    Timer().start()
