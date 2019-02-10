from ..base import FFmpegFile


class WebmFile(FFmpegFile):

    SUPPORTED_TYPES = ("video/webm",)

    def sign(self, private_key, domain: str) -> None:

        self.require_ffmpeg_version(
            "3.4", "Signing Webm files requires FFmpeg version {} or higher.")

        return super().sign(private_key, domain)

    def _get_suffix(self) -> str:
        return "webm"
