package com.taba.lawro.data_class

import com.google.gson.annotations.SerializedName
import java.util.Date

data class ChatMessage(
    @SerializedName("role")
    val role: String, // "user" 또는 "assistant"
    
    @SerializedName("content")
    val content: String, // 메시지 내용
    
    @SerializedName("timestamp")
    val timestamp: Date = Date(),
    
    // UI를 위한 추가 필드들
    val isTyping: Boolean = false
) {
    // 편의 메서드들
    val isUser: Boolean
        get() = role == "user"
    
    val text: String
        get() = content
}
