package com.taba.lawro.navigation.chatbot

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.graphics.Color
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.taba.lawro.data_class.ChatMessage
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.sp
import android.util.Log
import com.taba.lawro.R
import com.taba.lawro.repository.LawRoRepository
import com.taba.lawro.selectLanguage.LanguageManager
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatbotScreen() {
    val messages = remember { mutableStateListOf<ChatMessage>() }
    var input by remember { mutableStateOf("") }
    val scope = rememberCoroutineScope()
    val repository = remember { LawRoRepository() }
    var currentSessionId by remember { mutableStateOf<String?>(null) }
    
    // 앱 시작시 새 세션 생성
    LaunchedEffect(Unit) {
        repository.createNewSession()
            .onSuccess { sessionResponse ->
                currentSessionId = sessionResponse.sessionId
                Log.d("ChatbotScreen", "새 세션 생성됨: ${sessionResponse.sessionId}")
            }
            .onFailure { error ->
                Log.e("ChatbotScreen", "세션 생성 실패", error)
            }
    }

    Scaffold(
        bottomBar = {
            Surface(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(8.dp),
                shape = RoundedCornerShape(12.dp),
                color = Color.White,
                tonalElevation = 2.dp,
                shadowElevation = 4.dp
            ) {
                Row(
                    modifier = Modifier.padding(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    TextField(
                        value = input,
                        onValueChange = { input = it },
                        modifier = Modifier.weight(1f),
                        placeholder = { Text("메시지를 입력하세요") },
                        colors = TextFieldDefaults.colors(
                            focusedContainerColor = Color.Transparent,
                            unfocusedContainerColor = Color.Transparent,
                            focusedIndicatorColor = Color.Transparent,
                            unfocusedIndicatorColor = Color.Transparent
                        )
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .clip(CircleShape)
                            .background(Color(0xFF0C8FF6))
                            .shadow(4.dp, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        val context = LocalContext.current
                        val language = LanguageManager.getLanguage(context)
                        IconButton(onClick = {
                            if (input.isNotBlank()) {
                                val userMessage = input
                                messages.add(ChatMessage(
                                    role = "user",
                                    content = userMessage
                                ))
                                input = ""

                                val typingMsg = ChatMessage(
                                    role = "assistant",
                                    content = "작성중...",
                                    isTyping = true
                                )
                                messages.add(typingMsg)

                                scope.launch {
                                    repository.sendMessage(
                                        message = userMessage,
                                        language = language,
                                        sessionId = currentSessionId
                                    )
                                    .onSuccess { response ->
                                        messages.remove(typingMsg)
                                        messages.add(ChatMessage(
                                            role = "assistant",
                                            content = response.message
                                        ))
                                        
                                        Log.d("ChatbotScreen", "AI 응답: ${response.message}")
                                        Log.d("ChatbotScreen", "처리 시간: ${response.processingTime}초")
                                    }
                                    .onFailure { error ->
                                        messages.remove(typingMsg)
                                        messages.add(ChatMessage(
                                            role = "assistant",
                                            content = "서버 오류가 발생했어요: ${error.message}"
                                        ))
                                        Log.e("ChatbotScreen", "메시지 전송 실패", error)
                                    }
                                }
                            }
                        }) {
                            Icon(
                                painter = if (input.isBlank())
                                    painterResource(R.drawable.ic_send_isblanked)
                                else
                                    painterResource(R.drawable.ic_send_isnotblanked),
                                contentDescription = "전송",
                                tint = Color.White
                            )
                        }
                    }
                }
            }
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 8.dp)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 16.dp)
                    .offset(y = (-50).dp),
                contentAlignment = Alignment.Center
            ) {
                Text("상담 챗봇", fontSize = 18.sp)
            }

            LazyColumn(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                items(messages) { msg ->
                    ChatBubble(msg)
                }
            }
        }
    }
}
