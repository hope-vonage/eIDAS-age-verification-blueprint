from idpyoidc.server.user_authn.user import PidIssuerAuth, create_signed_jwt
from flask import redirect
import json


class VonageOidcAuth(PidIssuerAuth):
    def __call__(self, **kwargs):
        print("Welcome to Vonage OIDC Authentication")
        _context = self.upstream_get("context")
        _keyjar = self.upstream_get("attribute", "keyjar")
        # Filter out non-JSON-serializable values (e.g. class objects) before
        # creating the signed JWT, exactly as the parent class expects
        def _serializable(v):
            try:
                json.dumps(v)
                return True
            except (TypeError, ValueError):
                return False
        safe_kwargs = {k: v for k, v in kwargs.items() if _serializable(v)}
        jws = create_signed_jwt(_context.issuer, _keyjar, **safe_kwargs)
        return redirect(f"/phone_form?jws_token={jws}")
