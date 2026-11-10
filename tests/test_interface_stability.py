"""Regresiones de interfaz: traduccion externa y estado del agente."""
from pathlib import Path
import unittest


class TestInterfaceStability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = Path("app.py").read_text(encoding="utf-8")

    def test_chat_does_not_seed_stale_rules_message(self):
        self.assertIn('st.session_state.chat_history = []', self.source)
        self.assertNotIn(
            '"el chat utiliza reglas y todavía no es un modelo de IA."',
            self.source,
        )

    def test_existing_stale_welcome_is_migrated(self):
        self.assertIn(
            'and "el chat utiliza reglas" in str(',
            self.source,
        )
        self.assertIn(
            'st.session_state.chat_history = st.session_state.chat_history[1:]',
            self.source,
        )

    def test_agent_warns_when_not_configured(self):
        self.assertIn(
            'if ai_configured():',
            self.source,
        )
        self.assertIn(
            'El agente de IA está desactivado porque falta configurar OPENAI_API_KEY',
            self.source,
        )

    def test_edge_translation_instructions_are_in_sidebar(self):
        self.assertIn('¿Error al cambiar de pantalla en Edge?', self.source)
        self.assertIn('Nunca traducir este sitio', self.source)

    def test_custom_html_prevents_translation(self):
        self.assertIn('notranslate" translate="no"', self.source)
        self.assertIn('class="logo notranslate" translate="no"', self.source)


if __name__ == "__main__":
    unittest.main()
