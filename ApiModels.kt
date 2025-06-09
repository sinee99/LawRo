import com.google.gson.annotations.SerializedName
import java.util.Date

// 채팅 메시지 모델
data class ChatMessage(
    @SerializedName("role")
    val role: String,
    
    @SerializedName("content")
    val content: String,
    
    @SerializedName("timestamp")
    val timestamp: Date
)

// 채팅 요청 모델
data class ChatRequest(
    @SerializedName("message")
    val message: String,
    
    @SerializedName("session_id")
    val sessionId: String? = null,
    
    @SerializedName("context")
    val context: String? = null,
    
    @SerializedName("custom_prompt")
    val customPrompt: String? = null,
    
    @SerializedName("user_language")
    val userLanguage: String = "korean"
)

// 채팅 응답 모델
data class ChatResponse(
    @SerializedName("success")
    val success: Boolean,
    
    @SerializedName("message")
    val message: String,
    
    @SerializedName("chat_history")
    val chatHistory: List<ChatMessage>,
    
    @SerializedName("processing_time")
    val processingTime: Double
)

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