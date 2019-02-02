from abc import ABC, abstractmethod


class SpeechToText(ABC):

    @abstractmethod
    def recognize(self, audio, language):
        pass

    @abstractmethod
    def recognize_from_url(self, audio_url, language):
        pass
