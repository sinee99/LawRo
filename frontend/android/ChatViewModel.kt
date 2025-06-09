package com.taba.lawro.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.taba.lawro.data_class.ChatMessage
import com.taba.lawro.repository.LawRoRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ChatViewModel : ViewModel() {
    
    private val repository = LawRoRepository()
    
    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    private val _sessionId = MutableStateFlow<String?>(null)
    val sessionId: StateFlow<String?> = _sessionId.asStateFlow()
    
    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()
    
    init {
        createNewSession()
    }
    
    /**
     * 새로운 세션 생성
     */
    fun createNewSession() {
        viewModelScope.launch {
            repository.createNewSession()
                .onSuccess { sessionResponse ->
                    _sessionId.value = sessionResponse.sessionId
                    _messages.value = emptyList() // 새 세션이면 메시지 초기화
                }
                .onFailure { error ->
                    _errorMessage.value = "세션 생성 실패: ${error.message}"
                }
        }
    }
    
    /**
     * 메시지 전송
     */
    fun sendMessage(
        message: String,
        language: String = "korean",
        context: String? = null,
        customPrompt: String? = null
    ) {
        if (message.isBlank()) return
        
        // 사용자 메시지 추가
        val userMessage = ChatMessage(role = "user", content = message)
        _messages.value = _messages.value + userMessage
        
        // 타이핑 메시지 추가
        val typingMessage = ChatMessage(
            role = "assistant", 
            content = "작성중...", 
            isTyping = true
        )
        _messages.value = _messages.value + typingMessage
        
        _isLoading.value = true
        
        viewModelScope.launch {
            repository.sendMessage(
                message = message,
                language = language,
                sessionId = _sessionId.value,
                context = context,
                customPrompt = customPrompt
            )
            .onSuccess { response ->
                // 타이핑 메시지 제거 후 실제 응답 추가
                _messages.value = _messages.value.filter { !it.isTyping }
                
                val assistantMessage = ChatMessage(
                    role = "assistant",
                    content = response.message
                )
                _messages.value = _messages.value + assistantMessage
                
                _errorMessage.value = null
            }
            .onFailure { error ->
                // 타이핑 메시지 제거 후 오류 메시지 추가
                _messages.value = _messages.value.filter { !it.isTyping }
                
                val errorMsg = ChatMessage(
                    role = "assistant",
                    content = "오류가 발생했습니다: ${error.message}"
                )
                _messages.value = _messages.value + errorMsg
                
                _errorMessage.value = error.message
            }
            .also {
                _isLoading.value = false
            }
        }
    }
    
    /**
     * 계약서 분석을 위한 메시지 전송
     */
    fun sendMessageWithContract(
        message: String,
        contractContent: String,
        language: String = "korean"
    ) {
        sendMessage(
            message = message,
            language = language,
            context = contractContent,
            customPrompt = "주어진 계약서 내용을 바탕으로 상세하고 정확한 법률 조언을 제공해주세요."
        )
    }
    
    /**
     * 채팅 히스토리 로드
     */
    fun loadChatHistory() {
        val sessionId = _sessionId.value ?: return
        
        viewModelScope.launch {
            repository.getChatHistory(sessionId)
                .onSuccess { historyResponse ->
                    _messages.value = historyResponse.chatHistory
                }
                .onFailure { error ->
                    _errorMessage.value = "히스토리 로드 실패: ${error.message}"
                }
        }
    }
    
    /**
     * 오류 메시지 클리어
     */
    fun clearErrorMessage() {
        _errorMessage.value = null
    }
    
    /**
     * 서버 연결 상태 확인
     */
    fun checkServerConnection(onResult: (Boolean) -> Unit) {
        viewModelScope.launch {
            repository.checkServerHealth()
                .onSuccess { isHealthy ->
                    onResult(isHealthy)
                }
                .onFailure {
                    onResult(false)
                }
        }
    }
} 