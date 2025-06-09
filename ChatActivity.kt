import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class ChatActivity : AppCompatActivity() {
    
    private val repository = LawRoRepository()
    private var currentSessionId: String? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chat)
        
        // 앱 시작시 새 세션 생성
        createNewChatSession()
        
        // 예제: 메시지 전송 버튼 클릭 리스너
        // sendButton.setOnClickListener {
        //     val message = messageEditText.text.toString().trim()
        //     if (message.isNotEmpty()) {
        //         sendChatMessage(message, "korean")
        //     }
        // }
    }
    
    /**
     * 새로운 채팅 세션 생성
     */
    private fun createNewChatSession() {
        lifecycleScope.launch {
            repository.createNewSession()
                .onSuccess { sessionResponse ->
                    currentSessionId = sessionResponse.sessionId
                    Log.d("ChatActivity", "새 세션 생성됨: ${sessionResponse.sessionId}")
                    Toast.makeText(this@ChatActivity, "새로운 채팅을 시작합니다", Toast.LENGTH_SHORT).show()
                }
                .onFailure { error ->
                    Log.e("ChatActivity", "세션 생성 실패", error)
                    Toast.makeText(this@ChatActivity, "세션 생성에 실패했습니다: ${error.message}", Toast.LENGTH_LONG).show()
                }
        }
    }
    
    /**
     * 채팅 메시지 전송 (기본 한국어)
     */
    private fun sendChatMessage(message: String, language: String = "korean") {
        lifecycleScope.launch {
            // 로딩 표시
            showLoading(true)
            
            repository.sendMessage(
                message = message,
                language = language,
                sessionId = currentSessionId
            )
            .onSuccess { chatResponse ->
                Log.d("ChatActivity", "메시지 전송 성공")
                
                // UI 업데이트
                updateChatUI(chatResponse)
                
                // 성공 메시지
                Toast.makeText(this@ChatActivity, "응답 처리 완료", Toast.LENGTH_SHORT).show()
            }
            .onFailure { error ->
                Log.e("ChatActivity", "메시지 전송 실패", error)
                Toast.makeText(this@ChatActivity, "메시지 전송 실패: ${error.message}", Toast.LENGTH_LONG).show()
            }
            .also {
                // 로딩 숨김
                showLoading(false)
            }
        }
    }
    
    /**
     * 특정 언어로 메시지 전송
     */
    private fun sendMessageInLanguage(message: String, language: String) {
        lifecycleScope.launch {
            showLoading(true)
            
            repository.sendMessage(
                message = message,
                language = language,
                sessionId = currentSessionId
            )
            .onSuccess { chatResponse ->
                updateChatUI(chatResponse)
                Log.d("ChatActivity", "[$language] 응답: ${chatResponse.message}")
            }
            .onFailure { error ->
                Log.e("ChatActivity", "[$language] 메시지 전송 실패", error)
                Toast.makeText(this@ChatActivity, "메시지 전송 실패: ${error.message}", Toast.LENGTH_LONG).show()
            }
            .also {
                showLoading(false)
            }
        }
    }
    
    /**
     * 계약서 분석을 위한 컨텍스트 포함 메시지 전송
     */
    private fun sendMessageWithContext(message: String, contractContent: String, language: String = "korean") {
        lifecycleScope.launch {
            showLoading(true)
            
            repository.sendMessage(
                message = message,
                language = language,
                sessionId = currentSessionId,
                context = contractContent,  // 계약서 내용을 컨텍스트로 전달
                customPrompt = "주어진 계약서 내용을 바탕으로 상세하고 정확한 법률 조언을 제공해주세요."
            )
            .onSuccess { chatResponse ->
                updateChatUI(chatResponse)
                Log.d("ChatActivity", "계약서 분석 완료")
            }
            .onFailure { error ->
                Log.e("ChatActivity", "계약서 분석 실패", error)
                Toast.makeText(this@ChatActivity, "계약서 분석 실패: ${error.message}", Toast.LENGTH_LONG).show()
            }
            .also {
                showLoading(false)
            }
        }
    }
    
    /**
     * 채팅 히스토리 조회
     */
    private fun loadChatHistory() {
        currentSessionId?.let { sessionId ->
            lifecycleScope.launch {
                repository.getChatHistory(sessionId)
                    .onSuccess { historyResponse ->
                        Log.d("ChatActivity", "히스토리 로드 완료: ${historyResponse.messageCount}개")
                        // UI에 채팅 히스토리 표시
                        displayChatHistory(historyResponse.chatHistory)
                    }
                    .onFailure { error ->
                        Log.e("ChatActivity", "히스토리 로드 실패", error)
                    }
            }
        }
    }
    
    /**
     * 서버 연결 상태 확인
     */
    private fun checkServerConnection() {
        lifecycleScope.launch {
            repository.checkServerHealth()
                .onSuccess { isHealthy ->
                    val message = if (isHealthy) "서버 연결 정상" else "서버 연결 불안정"
                    Toast.makeText(this@ChatActivity, message, Toast.LENGTH_SHORT).show()
                }
                .onFailure { error ->
                    Toast.makeText(this@ChatActivity, "서버 연결 확인 실패: ${error.message}", Toast.LENGTH_LONG).show()
                }
        }
    }
    
    // UI 관련 메서드들 (구현 필요)
    private fun showLoading(show: Boolean) {
        // 로딩 인디케이터 표시/숨김
        // progressBar.visibility = if (show) View.VISIBLE else View.GONE
    }
    
    private fun updateChatUI(chatResponse: ChatResponse) {
        // 채팅 UI 업데이트
        // - 사용자 메시지와 AI 응답을 RecyclerView에 추가
        // - 채팅 히스토리 업데이트
        Log.d("ChatActivity", "AI 응답: ${chatResponse.message}")
        Log.d("ChatActivity", "처리 시간: ${chatResponse.processingTime}초")
        
        // 예제: RecyclerView에 메시지 추가
        // chatAdapter.addMessages(chatResponse.chatHistory)
        // chatRecyclerView.scrollToPosition(chatAdapter.itemCount - 1)
    }
    
    private fun displayChatHistory(chatHistory: List<ChatMessage>) {
        // 채팅 히스토리를 UI에 표시
        // chatAdapter.updateMessages(chatHistory)
    }
}

// 사용 예제들:

// 1. 기본 한국어 메시지
// sendChatMessage("근로계약서에서 주의해야 할 점은 무엇인가요?")

// 2. 영어 메시지
// sendMessageInLanguage("What should I be careful about in employment contracts?", "english")

// 3. 중국어 메시지
// sendMessageInLanguage("在劳动合同中应该注意什么？", "chinese")  

// 4. 베트남어 메시지
// sendMessageInLanguage("Những điều cần lưu ý trong hợp đồng lao động là gì?", "vietnamese")

// 5. 계약서 분석
// val contractText = "근로계약서 내용..."
// sendMessageWithContext("이 계약서에 문제가 있나요?", contractText) 