import uuid
from flask import jsonify, request
from src.llm.memory.conversation_memory import ConversationMemory
from src.llm.models.llm_message import LlmMessage
from src.llm.service.openai_llm_response_service import OpenAILlmResponseService
from src.agent.search_agent import SearchAgent
from src.agent.conversation_agent import ConversationAgent
from src.rest.dto.conversation_dto import (
    CreateConversationRequest,
    CreateConversationResponse,
    ContinueConversationRequest,
    ContinueConversationResponse
)


def clanker_routes(app):
    """Register all clanker related routes"""
    llm_service = OpenAILlmResponseService()
    search_agent = SearchAgent(llm_service)
    conversation_agent = ConversationAgent(llm_service)
    memory = ConversationMemory()

    @app.route('/v1/conversation', methods=['POST'])
    def create_conversation():
        """
        Create a new conversation
        :return: JSON response including conversation ID and response message
        """
        try:
            data = request.get_json()
            if not data or 'user_request' not in data:
                return jsonify({'error': 'user_request is required'}), 400
            
            req = CreateConversationRequest(user_request=data['user_request'])
            
            conversation_id = uuid.uuid4()
            response_message = search_agent.execute(req.user_request)
            
            memory.add(conversation_id, LlmMessage(role="user", content=req.user_request))
            memory.add(conversation_id, LlmMessage(role="assistant", content=response_message))

            response = CreateConversationResponse(
                conversation_id=conversation_id,
                response_message=response_message
            )
            
            return jsonify({
                'conversation_id': response.conversation_id,
                'response_message': response.response_message
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/v1/conversation', methods=['PATCH'])
    def continue_conversation():
        """
        Continue an existing conversation based off the conversation ID provided in the request body
        :return: JSON response including response message
        """
        try:
            data = request.get_json()
            if not data or 'conversation_id' not in data or 'user_request' not in data:
                return jsonify({'error': 'conversation_id and user_request are required'}), 400
            
            req = ContinueConversationRequest(
                conversation_id=data['conversation_id'],
                user_request=data['user_request']
            )

            conversation_uuid = req.conversation_id
            conversation_history = memory.history(conversation_uuid)

            response_message = conversation_agent.execute(
                req.user_request, 
                conversation_history=conversation_history
            )

            memory.add(conversation_uuid, LlmMessage(role="user", content=req.user_request))
            memory.add(conversation_uuid, LlmMessage(role="assistant", content=response_message))

            response = ContinueConversationResponse(response_message=response_message)
            
            return jsonify({
                'response_message': response.response_message
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


