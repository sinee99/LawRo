import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class LawRoRepository {
    
    private val apiService = ApiClient.apiService
    
    /**
     * 채팅 메시지 전송
     * @param message 사용자 메시지
     * @param language 사용자 언어 (korean, english, chinese, vietnamese 등)
     * @param sessionId 세션 ID (옵션)
     * @param context 컨텍스트 정보 (계약서 내용 등, 옵션)
     * @param customPrompt 커스터마이즈된 프롬프트 (옵션)
     */
    suspend fun sendMessage(
        message: String,
        language: String = "korean",
        sessionId: String? = null,
        context: String? = null,
        customPrompt: String? = null
    ): Result<ChatResponse> {
        return withContext(Dispatchers.IO) {
            try {
                val request = ChatRequest(
                    message = message,
                    sessionId = sessionId,
                    context = context,
                    customPrompt = customPrompt,
                    userLanguage = language
                )
                
                Log.d("LawRoRepository", "메시지 전송 시작: $message")
                val response = apiService.sendChatMessage(request)
                
                if (response.isSuccessful) {
                    response.body()?.let { chatResponse ->
                        Log.d("LawRoRepository", "응답 성공: ${chatResponse.message}")
                        Result.success(chatResponse)
                    } ?: Result.failure(Exception("응답 데이터가 비어있습니다"))
                } else {
                    Log.e("LawRoRepository", "API 오류: ${response.code()} - ${response.message()}")
                    Result.failure(Exception("API 호출 실패: ${response.code()} ${response.message()}"))
                }
            } catch (e: Exception) {
                Log.e("LawRoRepository", "네트워크 오류", e)
                Result.failure(e)
            }
        }
    }
    
    /**
     * 새로운 채팅 세션 생성
     */
    suspend fun createNewSession(): Result<SessionResponse> {
        return withContext(Dispatchers.IO) {
            try {
                Log.d("LawRoRepository", "새 세션 생성 시작")
                val response = apiService.createNewSession()
                
                if (response.isSuccessful) {
                    response.body()?.let { sessionResponse ->
                        Log.d("LawRoRepository", "세션 생성 성공: ${sessionResponse.sessionId}")
                        Result.success(sessionResponse)
                    } ?: Result.failure(Exception("세션 생성 응답이 비어있습니다"))
                } else {
                    Log.e("LawRoRepository", "세션 생성 실패: ${response.code()}")
                    Result.failure(Exception("세션 생성 실패: ${response.code()} ${response.message()}"))
                }
            } catch (e: Exception) {
                Log.e("LawRoRepository", "세션 생성 오류", e)
                Result.failure(e)
            }
        }
    }
    
    /**
     * 채팅 히스토리 조회
     */
    suspend fun getChatHistory(sessionId: String): Result<ChatHistoryResponse> {
        return withContext(Dispatchers.IO) {
            try {
                Log.d("LawRoRepository", "채팅 히스토리 조회: $sessionId")
                val response = apiService.getChatHistory(sessionId)
                
                if (response.isSuccessful) {
                    response.body()?.let { historyResponse ->
                        Log.d("LawRoRepository", "히스토리 조회 성공: ${historyResponse.messageCount}개 메시지")
                        Result.success(historyResponse)
                    } ?: Result.failure(Exception("히스토리 응답이 비어있습니다"))
                } else {
                    Log.e("LawRoRepository", "히스토리 조회 실패: ${response.code()}")
                    Result.failure(Exception("히스토리 조회 실패: ${response.code()} ${response.message()}"))
                }
            } catch (e: Exception) {
                Log.e("LawRoRepository", "히스토리 조회 오류", e)
                Result.failure(e)
            }
        }
    }
    
    /**
     * 서버 상태 확인
     */
    suspend fun checkServerHealth(): Result<Boolean> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.healthCheck()
                Result.success(response.isSuccessful)
            } catch (e: Exception) {
                Log.e("LawRoRepository", "서버 상태 확인 오류", e)
                Result.failure(e)
            }
        }
    }
} 