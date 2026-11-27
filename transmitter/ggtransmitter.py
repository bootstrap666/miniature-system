import ggwave
import pyaudio


class GGWaveTransmitter:
    """Transmissor síncrono que ignora mensagens acima do limite do protocolo."""

    MAX_BYTES = 140

    def __init__(
        self, 
        protocol_id: int = 0, 
        volume: int = 20, 
        sample_rate: int = 48000
    ):
        self.protocol_id = protocol_id
        self.volume = volume
        self.sample_rate = sample_rate
        self._pyaudio = pyaudio.PyAudio()
        self._stream = self._pyaudio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            output=True,
        )
        params = ggwave.getDefaultParameters()
        params["sampleRateInput"] = sample_rate
        self._instance = ggwave.init(params)

    def send(
        self, 
        message: str
        ) -> bool:
        """Valida o tamanho e transmite. Retorna False se a mensagem for ignorada."""
        byte_len = len(message.encode("utf-8"))

        if byte_len == 0:
            return False

        if byte_len > self.MAX_BYTES:
            print(f"[Alerta] Mensagem longa demais ({byte_len}/{self.MAX_BYTES} bytes). Ignorada.")
            return False

        waveform = ggwave.encode(
            message,
            protocolId=self.protocol_id,
            volume=self.volume,
        )
        self._stream.write(waveform)
        return True

    def close(self) -> None:
        if self._stream.is_active():
            self._stream.stop_stream()
        self._stream.close()
        self._pyaudio.terminate()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


if __name__ == "__main__":
    with GGWaveTransmitter(protocol_id=0, volume=25) as tx:
        print(f"=== Transmissor ggwave (Audible Normal | Máx: {tx.MAX_BYTES} bytes) ===")
        print("Digite sua mensagem e pressione Enter.\n")

        try:
            while True:
                texto = input("> ").strip()

                if texto.lower() in ("sair", "exit", "quit"):
                    break

                if tx.send(texto):
                    print("Enviado!\n")

        except KeyboardInterrupt:
            print("\nEncerrando...")
