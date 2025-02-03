def stop(self) -> None:
        packet = self.stream.encode(None)
        self.output.mux(packet)
        self.output.close()