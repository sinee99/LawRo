import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface LawRoApiService {
    
    // 채팅 메시지 전송
    @POST("chat/send")
    suspend fun sendChatMessage(@Body request: ChatRequest): Response<ChatResponse>
    
    // 새로운 세션 생성
    @POST("chat/new-session")
    suspend fun createNewSession(): Response<SessionResponse>
    
    // 채팅 히스토리 조회
    @GET("chat/history/{session_id}")
    suspend fun getChatHistory(@Path("session_id") sessionId: String): Response<ChatHistoryResponse>
    
    // 헬스 체크
    @GET("health")
    suspend fun healthCheck(): Response<Map<String, Any>>
} 