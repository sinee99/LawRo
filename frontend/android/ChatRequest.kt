package com.taba.lawro.data_class

import com.google.gson.annotations.SerializedName

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