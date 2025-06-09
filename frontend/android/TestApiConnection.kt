package com.taba.lawro.test

import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import com.taba.lawro.network.RetrofitClient

object TestApiConnection {
    
    fun testServerConnection() {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                Log.d("ApiTest", "서버 연결 테스트 시작...")
                
                // 1. 헬스 체크
                val healthResponse = RetrofitClient.apiService.healthCheck()
                if (healthResponse.isSuccessful) {
                    Log.d("ApiTest", "✅ 헬스 체크 성공: ${healthResponse.body()}")
                } else {
                    Log.e("ApiTest", "❌ 헬스 체크 실패: ${healthResponse.code()}")
                }
                
                // 2. 세션 생성 테스트
                val sessionResponse = RetrofitClient.apiService.createNewSession()
                if (sessionResponse.isSuccessful) {
                    val session = sessionResponse.body()
                    Log.d("ApiTest", "✅ 세션 생성 성공: ${session?.sessionId}")
                } else {
                    Log.e("ApiTest", "❌ 세션 생성 실패: ${sessionResponse.code()} - ${sessionResponse.message()}")
                    Log.e("ApiTest", "응답 바디: ${sessionResponse.errorBody()?.string()}")
                }
                
            } catch (e: Exception) {
                Log.e("ApiTest", "❌ 네트워크 오류: ${e.message}", e)
            }
        }
    }
} 