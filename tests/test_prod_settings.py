import importlib


def test_prod_site_domain_is_sailwithme_net():
    from config.settings import prod

    importlib.reload(prod)

    assert prod.SITE_DOMAIN == "sailwithme.net"
    assert "sailwithme.net" in prod.ALLOWED_HOSTS
    assert "www.sailwithme.net" in prod.ALLOWED_HOSTS
    assert prod.CSRF_TRUSTED_ORIGINS == [
        "https://sailwithme.net",
        "https://www.sailwithme.net",
    ]
    assert prod.ACCOUNT_DEFAULT_HTTP_PROTOCOL == "https"
    assert prod.DEFAULT_FROM_EMAIL.endswith("@sailwithme.net>")
