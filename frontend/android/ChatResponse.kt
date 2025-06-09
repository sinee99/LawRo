package com.taba.lawro.data_class

import com.google.gson.annotations.SerializedName

data class ChatResponse(
    @SerializedName("success")
    val success: Boolean,
    
    @SerializedName("message")
    val message: String,
    
    @SerializedName("chat_history")
    val chatHistory: List<ChatMessage>,
    
    @SerializedName("processing_time")
    val processingTime: Double
) {
    // 기존 코드와의 호환성을 위한 편의 프로퍼티
    val reply: String
        get() = message
}

// 세션 생성 응답 모델
data class SessionResponse(
    @SerializedName("success")
    val success: Boolean,
    
    @SerializedName("session_id")
    val sessionId: String,
    
    @SerializedName("message")
    val message: String
)

// 채팅 히스토리 응답 모델  
data class ChatHistoryResponse(
    @SerializedName("success")
    val success: Boolean,
    
    @SerializedName("session_id")
    val sessionId: String,
    
    @SerializedName("chat_history")
    val chatHistory: List<ChatMessage>,
    
    @SerializedName("message_count")
    val messageCount: Int
)
