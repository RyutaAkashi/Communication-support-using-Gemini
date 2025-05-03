import usb.core  # type: ignore
import usb.util  # type: ignore
import struct
import pyaudio
import wave
from queue import Queue
from collections import deque
from threading import Thread


class SoundRecorder:
    PARAMETERS = {
        "DOAANGLE": (
            21,
            0,
            "int",
            359,
            0,
            "ro",
            "DOA angle. Current value. \
            Orientation depends on build configuration.",
        ),
        "SPEECHDETECTED": (
            19,
            22,
            "int",
            1,
            0,
            "ro",
            "Speech detection status.",
            "0 = false (no speech detected)",
            "1 = true (speech detected)",
        ),
    }

    DEVICE = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    TIMEOUT = 100000
    RESPEAKER_RATE = 16000
    RESPEAKER_CHANNELS = 1
    RESPEAKER_WIDTH = 2
    RESPEAKER_INDEX = 1      # マイクのindex数
    CHUNK = 1024
    DEQUE_SIZE = 6

    def __init__(self, file_path_queue: Queue, voice_angle_queue: Queue):
        self.file_number = 0
        self.p = pyaudio.PyAudio()
        self.ring_buffer: deque = deque([], maxlen=self.DEQUE_SIZE)
        self.chunk_queue: Queue = Queue()
        self.frames: list[bytes] = []
        self.file_path_queue = file_path_queue
        self.voice_angle_queue = voice_angle_queue

        # オーディオデバイスの確認とリスト表示
        self.list_audio_devices()

    def list_audio_devices(self):
        device_count = self.p.get_device_count()
        print("\n--- Audio Devices ---")
        for i in range(device_count):
            device_info = self.p.get_device_info_by_index(i)
            print(f"Device {i}: {device_info['name']}")

        print("---------------------\n")

    def read_parameter(self, param_name):
        try:
            data = self.PARAMETERS[param_name]
        except KeyError:
            return

        id = data[0]

        cmd = 0x80 | data[1]
        if data[2] == "int":
            cmd |= 0x40

        length = 8

        response = self.DEVICE.ctrl_transfer(
            usb.util.CTRL_IN
            | usb.util.CTRL_TYPE_VENDOR
            | usb.util.CTRL_RECIPIENT_DEVICE,
            0,
            cmd,
            id,
            length,
            self.TIMEOUT,
        )

        response = struct.unpack(b"ii", response.tobytes())

        if data[2] == "int":
            result = response[0]
        else:
            result = response[0] * (2.0 ** response[1])

        return result

    def audio_callback(self, in_data, frame_count, time_info, status):
        speech_detected = self.read_parameter("SPEECHDETECTED")
        self.chunk_queue.put((in_data, speech_detected))
        if speech_detected == 1:
            voice_angle = self.read_parameter("DOAANGLE")
            self.voice_angle_queue.put(voice_angle)
        return (in_data, pyaudio.paContinue)

    def start_recording(self):
        self.stream = self.p.open(
            rate=self.RESPEAKER_RATE,
            format=self.p.get_format_from_width(self.RESPEAKER_WIDTH),
            channels=self.RESPEAKER_CHANNELS,
            input=True,
            input_device_index=self.RESPEAKER_INDEX,
            stream_callback=self.audio_callback,
            frames_per_buffer=self.CHUNK
        )
        print("\n\n-- Start Stream --\n")

    def save_recorded_data(self):
        while not len(self.ring_buffer) == 0:
            self.frames.append(self.ring_buffer.popleft())
        wf = wave.open(str(self.file_number) + ".wav", "wb")
        wf.setnchannels(self.RESPEAKER_CHANNELS)
        wf.setsampwidth(
            self.p.get_sample_size(
                self.p.get_format_from_width(self.RESPEAKER_WIDTH)
            )
        )
        wf.setframerate(self.RESPEAKER_RATE)
        wf.writeframes(b"".join(self.frames))
        wf.close()
        self.frames = []
        print(" * Done Save!")
        self.file_path_queue.put(str(self.file_number) + ".wav")
        self.file_number += 1

    def run(self):
        try:
            while True:
                data, vad = self.chunk_queue.get()

                if vad == 1:
                    #print("* VAD : " + str(vad))
                    while not len(self.ring_buffer) == 0:
                        self.frames.append(self.ring_buffer.popleft())
                    self.frames.append(data)
                    print(" * Done Append!")

                else:
                    #print("* VAD : " + str(vad))
                    self.ring_buffer.append(data)
                    if (
                        self.frames
                        and len(self.ring_buffer) == self.DEQUE_SIZE
                    ):
                        self.save_recorded_data()
                    #else:
                        #print(" * Pending...")

        except Exception as e:
            print("\nExcept : " + str(e))

        finally:
            print("\nFinally!")
            print("\n-- Stop Stream  --")
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()


if __name__ == "__main__":

    def get_voice_angle(voice_angle_queue: Queue):
        while True:
            print(f"Voice_Angle : { voice_angle_queue.get() }")

    def get_file_name(file_name_queue: Queue):
        while True:
            print(f"File_Name : { file_name_queue.get() }")

    file_path_queue: Queue = Queue()
    voice_angle_queue: Queue = Queue()

    Thread(target=get_file_name, args=(file_path_queue,)).start()
    Thread(target=get_voice_angle, args=(voice_angle_queue,)).start()

    recorder = SoundRecorder(file_path_queue, voice_angle_queue)
    recorder.start_recording()
    recorder.run()
