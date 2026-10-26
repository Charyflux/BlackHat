import unittest
from unittest.mock import AsyncMock, patch

from open_webui.utils.minghat_recon import (
    extract_s3_references,
    extract_s3_technology_hosts,
    extract_target_hostnames,
    normalize_domain,
    normalize_recon_domain,
    recon_domain_allowed,
    requested_recon_domain,
    run_subfinder,
)


class MingHatReconTests(unittest.TestCase):
    def test_recon_only_runs_for_pentesting_model(self):
        messages = [{"role": "user", "content": "Faça um recon em exemplo.com"}]
        self.assertEqual(requested_recon_domain("kernel-unrestricted:latest", messages), "exemplo.com")
        self.assertIsNone(requested_recon_domain("uncensored-br:latest", messages))

    def test_recon_requires_explicit_intent(self):
        messages = [{"role": "user", "content": "O domínio exemplo.com usa HTTPS?"}]
        self.assertIsNone(requested_recon_domain("kernel-unrestricted:latest", messages))

    def test_domain_normalization_rejects_command_injection(self):
        self.assertEqual(normalize_domain("https://Alvo.com/path"), "alvo.com")
        self.assertEqual(normalize_domain("alvo.com"), "alvo.com")
        self.assertIsNone(normalize_domain("alvo.com&calc.exe"))

    def test_recon_normalization_uses_apex_when_user_types_www(self):
        self.assertEqual(normalize_recon_domain("https://www.multiplan.com.br/path"), "multiplan.com.br")
        messages = [{"role": "user", "content": "faça um recon no dominio www.multiplan.com.br"}]
        self.assertEqual(requested_recon_domain("kernel-unrestricted:latest", messages), "multiplan.com.br")

    def test_recon_rejects_local_and_rebinding_domains(self):
        self.assertFalse(recon_domain_allowed("metadata.google.internal"))
        self.assertFalse(recon_domain_allowed("127.0.0.1.nip.io"))
        self.assertFalse(recon_domain_allowed("alvo.local"))
        self.assertTrue(recon_domain_allowed("alvo.com.br"))

    def test_subfinder_output_keeps_only_target_subdomains(self):
        process = AsyncMock()
        process.communicate.return_value = (
            b"api.alvo.com\n[INF] verbose message\nother.example\nALVO.COM\n",
            b"diagnostic",
        )
        process.returncode = 0

        async def exercise():
            with patch("open_webui.utils.minghat_recon.find_subfinder", return_value="subfinder"), patch(
                "asyncio.create_subprocess_exec", return_value=process
            ):
                return await run_subfinder("alvo.com")

        result = __import__("asyncio").run(exercise())
        self.assertEqual(result["subdomains"], ["alvo.com", "api.alvo.com"])

    def test_subfinder_output_accepts_verbose_source_prefixes(self):
        text = "[submd] api.alvo.com\n[thc] dev.alvo.com\n[other] fora.example.com\n"
        self.assertEqual(extract_target_hostnames(text, "alvo.com"), ["api.alvo.com", "dev.alvo.com"])

    def test_subfinder_network_denied_is_not_reported_as_empty_success(self):
        process = AsyncMock()
        process.communicate.return_value = (
            b"",
            "Encountered an error: connectex: tentativa de acesso a uma socket proibida".encode(),
        )
        process.returncode = 0

        async def exercise():
            with patch("open_webui.utils.minghat_recon.find_subfinder", return_value="subfinder"), patch(
                "asyncio.create_subprocess_exec", return_value=process
            ):
                return await run_subfinder("alvo.com")

        result = __import__("asyncio").run(exercise())
        self.assertFalse(result["ok"])
        self.assertIn("bloqueadas", result["error"])

    def test_s3_references_are_extracted_without_probing(self):
        text = "https://assets.s3.us-east-1.amazonaws.com/a.js https://s3.amazonaws.com/public-files/x"
        self.assertEqual(extract_s3_references(text), ["assets", "public-files"])

    def test_s3_technology_hosts_are_extracted_from_httpx(self):
        text = "https://portal.alvo.com [403] [Amazon CloudFront,Amazon S3,Amazon Web Services]"
        self.assertEqual(extract_s3_technology_hosts(text), ["portal.alvo.com"])


if __name__ == "__main__":
    unittest.main()
