import unittest
from unittest.mock import MagicMock, patch
import logging

# Context manager to suppress logs during testing
import logging
logging.disable(logging.CRITICAL)

class TestConfig(unittest.TestCase):
    def test_settings_load(self):
        # Override env vars for test to avoid dependency on .env file presence
        with patch.dict('os.environ', {
            'GROQ_API_KEY': 'test_key', 
            'MCP_SERVER_URL': 'http://test.local'
        }):
            from core.config import get_settings
            # clear cache to ensure we reload
            get_settings.cache_clear()
            settings = get_settings()
            self.assertTrue(hasattr(settings, "GROQ_API_KEY"))
            self.assertTrue(hasattr(settings, "MCP_SERVER_URL"))
        print("\n✅ Config Test Passed")

class TestPrompts(unittest.TestCase):
    def test_cypher_prompt_generation(self):
        from domain.prompts import PromptBuilder
        # Test generic GUID (synthea_id)
        messages = PromptBuilder.get_cypher_gen_messages("Find patient John", "123-abc")
        self.assertIn("MATCH (p:Patient {synthea_id: '123-abc'})", messages[0]['content'])
        
        # Test Integer ID (patient_no)
        messages_int = PromptBuilder.get_cypher_gen_messages("Find patient John", "1")
        self.assertIn("MATCH (p:Patient {patient_no: 1})", messages_int[0]['content'])

        # Test Doctor ID Context
        messages_doc = PromptBuilder.get_cypher_gen_messages("History", "123-abc", "doc-001")
        self.assertIn("TREATED_BY", messages_doc[0]['content'])
        self.assertIn("'doc-001'", messages_doc[0]['content'])
        
        print("\n✅ Prompt Builder Test Passed")

class TestRAGPipeline(unittest.TestCase):
    @patch('service.rag_pipeline.MCPConnection')
    @patch('service.rag_pipeline.GroqClient')
    def test_pipeline_sucess(self, MockGroq, MockDB):
        from service.rag_pipeline import GraphRAGService
        
        # Setup Mocks
        mock_db_instance = MockDB.return_value
        mock_llm_instance = MockGroq.return_value
        
        # Mock LLM returning valid Cypher
        mock_llm_instance.generate.side_effect = ["MATCH (p:Patient) RETURN p", "The patient is John."]
        
        # Mock DB returning data
        # Mimic the actual MCP return format (list of dicts, e.g. from JSON text)
        mock_db_instance.query.return_value = [{"n": {"id": "123", "name": "John Doe"}}]
        
        service = GraphRAGService()
        response = service.process_request("Who is this?", "123")
        
        # Verify Interactions
        # 1. LLM called to generate Cypher
        self.assertEqual(mock_llm_instance.generate.call_count, 2)
        # 2. DB called to execute Cypher
        mock_db_instance.query.assert_called_with("MATCH (p:Patient) RETURN p")
        
        print("\n✅ Pipeline Success Scenario Passed")

    @patch('service.rag_pipeline.MCPConnection')
    @patch('service.rag_pipeline.GroqClient')
    def test_pipeline_retry_logic(self, MockGroq, MockDB):
        from service.rag_pipeline import GraphRAGService
        
        mock_db_instance = MockDB.return_value
        mock_llm_instance = MockGroq.return_value

        # Mock LLM:
        # 1. Bad Cypher
        # 2. Corrected Cypher
        # 3. Final Summarization
        mock_llm_instance.generate.side_effect = ["BAD CYPHER", "SUMMARY"]
        mock_llm_instance.correct_cypher.return_value = "GOOD CYPHER"
        
        # Mock DB:
        # 1. First call fails
        # 2. Second call succeeds
        mock_db_instance.query.side_effect = [Exception("MCP Error"), [{"n": {"id": "123", "name": "John Doe"}}]]
        
        service = GraphRAGService()
        result = service.process_request("test")
        
        # Verify Retry Logic
        self.assertEqual(mock_llm_instance.correct_cypher.call_count, 1)
        self.assertEqual(mock_db_instance.query.call_count, 2)
        print("\n✅ Pipeline Retry Logic Passed")

if __name__ == '__main__':
    unittest.main()
