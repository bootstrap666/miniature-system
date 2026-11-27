import ggwave
import pyaudio


class GGWaveReceiver:
    """Receptor síncrono que escuta o microfone e decodifica mensagens ggwave."""

    def __init__(
        self, 
        sample_rate: int = 48000, 
        frames_per_buffer: int = 1024
    ):
        self._frames_per_buffer = frames_per_buffer
        self._pyaudio = pyaudio.PyAudio()
        self._instance = ggwave.init()
        self._stream = self._pyaudio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=sample_rate,
            input=True,
            frames_per_buffer=self._frames_per_buffer,
        )
        params = ggwave.getDefaultParameters()
        params["sampleRateInput"] = sample_rate
        self._instance = ggwave.init(params)

    def read_once(self) -> str | None:
        """Lê um bloco de áudio do microfone e tenta decodificar."""
        data = self._stream.read(
            self._frames_per_buffer, 
            exception_on_overflow=False
        )
        res = ggwave.decode(self._instance, data)
        if res is not None:
            try:
                return res.decode("utf-8")
            except UnicodeDecodeError:
                return None
        return None

    def listen(self) -> None:
        """Fica em loop contínuo escutando e imprimindo mensagens na tela."""
        print("=== Escutando... (Pressione Ctrl+C para sair) ===\n")
        try:
            while True:
                msg = self.read_once()
                if msg is not None:
                    print(f"[Recebido]: {msg}")
        except KeyboardInterrupt:
            print("\nEncerrando...")

    def close(self) -> None:
        if self._stream.is_active():
            self._stream.stop_stream()
        self._stream.close()
        ggwave.free(self._instance)
        self._pyaudio.terminate()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


if __name__ == "__main__":
    with GGWaveReceiver() as rx:
        rx.listen()
