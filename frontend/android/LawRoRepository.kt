package com.taba.lawro.repository

import android.util.Log
import com.taba.lawro.data_class.ChatRequest
import com.taba.lawro.data_class.ChatResponse
import com.taba.lawro.data_class.SessionResponse
import com.taba.lawro.data_class.ChatHistoryResponse
import com.taba.lawro.network.RetrofitClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class LawRoRepository {
    
    private val apiService = RetrofitClient.apiService
    
    /**
     * 채팅 메시지 전송 (기존 코드와 호환)
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
                
                Log.d("LawRoRepository", "메시지 전송: $message")
                val response = apiService.sendMessage(request)
                
                Log.d("LawRoRepository", "응답 성공: ${response.message}")
                Result.success(response)
                
            } catch (e: Exception) {
                Log.e("LawRoRepository", "메시지 전송 실패", e)
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
                Log.d("LawRoRepository", "새 세션 생성 시작 - 서버: http://16.176.26.197:8000/")
                val response = apiService.createNewSession()
                
                Log.d("LawRoRepository", "응답 코드: ${response.code()}")
                Log.d("LawRoRepository", "응답 메시지: ${response.message()}")
                
                if (response.isSuccessful) {
                    response.body()?.let { sessionResponse ->
                        Log.d("LawRoRepository", "세션 생성 성공: ${sessionResponse.sessionId}")
                        Result.success(sessionResponse)
                    } ?: Result.failure(Exception("세션 생성 응답이 비어있습니다"))
                } else {
                    val errorBody = response.errorBody()?.string()
                    Log.e("LawRoRepository", "세션 생성 실패: ${response.code()} - ${response.message()}")
                    Log.e("LawRoRepository", "에러 바디: $errorBody")
                    Result.failure(Exception("세션 생성 실패: ${response.code()} ${response.message()}\n에러: $errorBody"))
                }
            } catch (e: Exception) {
                Log.e("LawRoRepository", "세션 생성 네트워크 오류: ${e.message}", e)
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