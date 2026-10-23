import base64
import hashlib

from chatgpt_auth import create_pkce_pair


def test_pkce_pair_uses_s256_without_padding():
    verifier, challenge = create_pkce_pair()
    expected = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest())
        .rstrip(b"=")
        .decode("ascii")
    )
    assert challenge == expected
    assert "=" not in challenge
    assert len(verifier) >= 43
