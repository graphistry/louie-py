"""``upload_image`` names the multipart part so the server can route it (#59).

The server dispatches uploads by filename extension and does not inspect the
bytes. A nameless ``io.BytesIO`` used to go up as ``image.bin`` because the
fallback name was fed to ``mimetypes``, which answered ``application/octet-stream``
(a real value, not ``None``), so the signature check never ran.
"""

import io
from unittest.mock import Mock

import pytest

from louieai._upload import UploadClient

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 16
GIF = b"GIF89a" + b"\x00" * 16
BMP = b"BM" + b"\x00" * 16
WEBP = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 16
UNKNOWN = b"not an image at all"


@pytest.fixture
def upload_client():
    return UploadClient(Mock())


class TestNamelessStream:
    """A stream with no name is named from its image signature."""

    @pytest.mark.parametrize(
        ("data", "expected"),
        [
            (PNG, ("image.png", "image/png")),
            (JPEG, ("image.jpg", "image/jpeg")),
            (GIF, ("image.gif", "image/gif")),
            (BMP, ("image.bmp", "image/bmp")),
            (WEBP, ("image.webp", "image/webp")),
        ],
    )
    def test_signature_names_the_file(self, upload_client, data, expected):
        """The bug: this used to return ('image.bin', 'application/octet-stream')."""
        _, filename, content_type = upload_client._serialize_image(io.BytesIO(data))
        assert (filename, content_type) == expected

    def test_bytes_and_stream_agree(self, upload_client):
        as_bytes = upload_client._serialize_image(PNG)
        as_stream = upload_client._serialize_image(io.BytesIO(PNG))
        assert as_bytes == as_stream

    @pytest.mark.parametrize(
        "data",
        [UNKNOWN, b"RIFF\x00\x00\x00\x00WAVEfmt ", b"\xff\xd8\x00" + b"\x00" * 16],
        ids=["text", "riff-wave", "two-byte-jpeg-prefix"],
    )
    def test_unknown_signature_stays_binary(self, upload_client, data):
        _, filename, content_type = upload_client._serialize_image(io.BytesIO(data))
        assert (filename, content_type) == ("image.bin", "application/octet-stream")

    def test_stream_is_rewound_for_the_caller(self, upload_client):
        stream = io.BytesIO(PNG)
        upload_client._serialize_image(stream)
        assert stream.tell() == 0


class TestDerivedName:
    """A derived name keeps an image extension; otherwise the signature picks one."""

    def test_image_extension_is_kept(self, upload_client):
        stream = io.BytesIO(PNG)
        stream.name = "/photos/shot.png"
        _, filename, content_type = upload_client._serialize_image(stream)
        assert (filename, content_type) == ("shot.png", "image/png")

    def test_image_extension_is_trusted_over_signature(self, upload_client):
        """Pre-existing behavior: a .png name is sent as PNG without sniffing."""
        stream = io.BytesIO(JPEG)
        stream.name = "shot.png"
        _, filename, content_type = upload_client._serialize_image(stream)
        assert (filename, content_type) == ("shot.png", "image/png")

    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("upload", "upload.jpg"),
            ("blob.bin", "blob.jpg"),
            ("data.dat", "data.jpg"),
            ("shot.txt", "shot.jpg"),
            ("shot.pdf", "shot.jpg"),
            ("/tmp/screenshot-2026-10-22.bin", "screenshot-2026-10-22.jpg"),
            ("archive.tar.gz", "archive.tar.jpg"),
            ("name.", "name.jpg"),
            (".hidden", ".hidden.jpg"),
            ("", "image.jpg"),
        ],
    )
    def test_non_image_extension_is_corrected_keeping_stem(
        self, upload_client, name, expected
    ):
        """The stem stays so a thread of uploads keeps distinct names."""
        stream = io.BytesIO(JPEG)
        stream.name = name
        _, filename, content_type = upload_client._serialize_image(stream)
        assert (filename, content_type) == (expected, "image/jpeg")

    @pytest.mark.parametrize("name", ["blob.dat", "notes.txt", "doc.pdf"])
    def test_non_image_extension_unknown_signature_keeps_name(
        self, upload_client, name
    ):
        """Not an image we recognize: keep the name, but don't claim a type."""
        stream = io.BytesIO(UNKNOWN)
        stream.name = name
        _, filename, content_type = upload_client._serialize_image(stream)
        assert (filename, content_type) == (name, "application/octet-stream")

    def test_empty_name_unknown_signature(self, upload_client):
        stream = io.BytesIO(UNKNOWN)
        stream.name = ""
        _, filename, content_type = upload_client._serialize_image(stream)
        assert (filename, content_type) == ("image.bin", "application/octet-stream")

    def test_integer_name_is_ignored(self, upload_client):
        """``open(fd).name`` can be an int."""
        stream = io.BytesIO(PNG)
        stream.name = 7
        _, filename, _ = upload_client._serialize_image(stream)
        assert filename == "image.png"

    def test_path_without_image_extension(self, upload_client, tmp_path):
        p = tmp_path / "capture.bin"
        p.write_bytes(PNG)
        _, filename, content_type = upload_client._serialize_image(str(p))
        assert (filename, content_type) == ("capture.png", "image/png")

    def test_path_without_extension(self, upload_client, tmp_path):
        p = tmp_path / "upload"
        p.write_bytes(PNG)
        _, filename, content_type = upload_client._serialize_image(p)
        assert (filename, content_type) == ("upload.png", "image/png")

    def test_path_object_unknown_signature(self, upload_client, tmp_path):
        p = tmp_path / "junk.txt"
        p.write_bytes(UNKNOWN)
        _, filename, content_type = upload_client._serialize_image(p)
        assert (filename, content_type) == ("junk.txt", "application/octet-stream")

    def test_path_with_image_extension(self, upload_client, tmp_path):
        p = tmp_path / "capture.png"
        p.write_bytes(PNG)
        _, filename, content_type = upload_client._serialize_image(str(p))
        assert (filename, content_type) == ("capture.png", "image/png")


class TestExplicitFilename:
    """``filename=`` is the caller's word and is sent verbatim."""

    def test_overrides_stream_name(self, upload_client):
        stream = io.BytesIO(PNG)
        stream.name = "shot.png"
        _, filename, content_type = upload_client._serialize_image(
            stream, "chart-q3.png"
        )
        assert (filename, content_type) == ("chart-q3.png", "image/png")

    def test_kept_even_without_image_extension(self, upload_client):
        """Verbatim, like upload_binary.

        The upload_image docstring asks callers to include an extension.
        """
        _, filename, content_type = upload_client._serialize_image(PNG, "capture")
        assert filename == "capture"
        assert content_type == "image/png"  # type still from the signature

    def test_pil_image_honors_filename(self, upload_client):
        Image = pytest.importorskip("PIL.Image")
        img = Image.new("RGB", (2, 2))
        _, filename, content_type = upload_client._serialize_image(img, "tiny.png")
        assert (filename, content_type) == ("tiny.png", "image/png")
        _, filename, _ = upload_client._serialize_image(img)
        assert filename == "image.png"

    def test_pil_jpeg_default_name(self, upload_client):
        Image = pytest.importorskip("PIL.Image")
        img = Image.new("RGB", (2, 2))
        img.format = "JPEG"
        _, filename, content_type = upload_client._serialize_image(img)
        assert (filename, content_type) == ("image.jpg", "image/jpeg")

    def test_kept_when_signature_unknown(self, upload_client):
        _, filename, content_type = upload_client._serialize_image(UNKNOWN, "x.dat")
        assert (filename, content_type) == ("x.dat", "application/octet-stream")

    def test_overrides_path_name(self, upload_client, tmp_path):
        p = tmp_path / "capture.bin"
        p.write_bytes(PNG)
        _, filename, content_type = upload_client._serialize_image(p, "chart.png")
        assert (filename, content_type) == ("chart.png", "image/png")

    def test_empty_means_unset(self, upload_client):
        """``filename=""`` falls back to the derived name, like ``None``."""
        stream = io.BytesIO(PNG)
        stream.name = "photo.jpg"
        _, filename, content_type = upload_client._serialize_image(stream, "")
        assert (filename, content_type) == ("photo.jpg", "image/jpeg")

    @pytest.mark.parametrize(
        "make", [lambda: PNG, lambda: io.BytesIO(PNG)], ids=["bytes", "stream"]
    )
    def test_empty_means_unset_nameless(self, upload_client, make):
        assert upload_client._serialize_image(make(), "")[1:] == (
            "image.png",
            "image/png",
        )

    def test_pil_empty_filename_means_unset(self, upload_client):
        Image = pytest.importorskip("PIL.Image")
        img = Image.new("RGB", (2, 2))
        assert upload_client._serialize_image(img, "")[1] == "image.png"
        img.format = "JPEG"
        assert upload_client._serialize_image(img, "")[1] == "image.jpg"

    @pytest.mark.parametrize(
        ("data", "given", "expected"),
        [
            (UNKNOWN, "x.png", ("x.png", "image/png")),
            (PNG, "a.jpg", ("a.jpg", "image/jpeg")),
        ],
        ids=["unknown-bytes", "bytes-disagree"],
    )
    def test_given_image_extension_sets_type(
        self, upload_client, data, given, expected
    ):
        assert upload_client._serialize_image(data, given)[1:] == expected

    def test_given_beats_derived_stream_name(self, upload_client):
        """A local name must not leak when the caller passes ``filename=``."""
        stream = io.BytesIO(PNG)
        stream.name = "/home/u/secret.bin"
        assert upload_client._serialize_image(stream, "capture")[1:] == (
            "capture",
            "image/png",
        )

    def test_given_beats_derived_path_name(self, upload_client, tmp_path):
        p = tmp_path / "secret.bin"
        p.write_bytes(PNG)
        assert upload_client._serialize_image(p, "capture")[1:] == (
            "capture",
            "image/png",
        )

    def test_upload_image_passes_filename_through(self, upload_client):
        upload_client._send_file = Mock()
        upload_client.upload_image("hi", io.BytesIO(PNG), filename="named.png")
        args = upload_client._send_file.call_args.args
        assert args[2:4] == ("named.png", "image/png")

    def test_cursor_forwards_filename(self):
        from louieai.notebook.cursor import Cursor

        client = Mock()
        client.upload_image.return_value = Mock(thread_id="D_1", elements=[])
        cursor = Cursor(client=client)
        cursor(PNG, "describe", filename="shot.png")  # lui(image, prompt) form
        client.upload_image.assert_called_once()
        assert client.upload_image.call_args.kwargs["filename"] == "shot.png"

    def test_cursor_forwards_filename_binary(self):
        """The binary branch has the same contract (sibling of the image test)."""
        from louieai.notebook.cursor import Cursor

        client = Mock()
        client.upload_binary.return_value = Mock(thread_id="D_1", elements=[])
        Cursor(client=client)(b"%PDF-1.4\n", "summarize", filename="report.pdf")
        assert client.upload_binary.call_args.kwargs["filename"] == "report.pdf"

    @pytest.mark.parametrize(
        ("method", "data"), [("upload_image", PNG), ("upload_binary", b"%PDF-1.4\n")]
    )
    def test_cursor_without_filename_forwards_none(self, method, data):
        from louieai.notebook.cursor import Cursor

        client = Mock()
        getattr(client, method).return_value = Mock(thread_id="D_1", elements=[])
        Cursor(client=client)(data, "describe")
        kwargs = getattr(client, method).call_args.kwargs
        assert "filename" in kwargs
        assert kwargs["filename"] is None

    def test_client_wrapper_accepts_filename(self):
        from louieai._client import LouieClient

        client = LouieClient(server_url="https://louie.test", graphistry_client=Mock())
        client._upload_client = Mock()
        client.upload_image("hi", PNG, filename="named.png")
        kwargs = client._upload_client.upload_image.call_args.kwargs
        assert kwargs["filename"] == "named.png"

    def test_client_wrapper_accepts_filename_binary(self):
        from louieai._client import LouieClient

        client = LouieClient(server_url="https://louie.test", graphistry_client=Mock())
        client._upload_client = Mock()
        client.upload_binary("hi", b"%PDF-1.4\n", filename="report.pdf")
        kwargs = client._upload_client.upload_binary.call_args.kwargs
        assert kwargs["filename"] == "report.pdf"

    @pytest.mark.parametrize(
        ("method", "data"), [("upload_image", PNG), ("upload_binary", b"%PDF-1.4\n")]
    )
    def test_client_wrapper_keeps_name_and_filename_apart(self, method, data):
        from louieai._client import LouieClient

        client = LouieClient(server_url="https://louie.test", graphistry_client=Mock())
        client._upload_client = Mock()
        getattr(client, method)("hi", data, name="thread", filename="named.bin")
        kwargs = getattr(client._upload_client, method).call_args.kwargs
        assert (kwargs["name"], kwargs["filename"]) == ("thread", "named.bin")
