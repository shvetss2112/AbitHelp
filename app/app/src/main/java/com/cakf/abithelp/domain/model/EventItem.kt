package com.cakf.abithelp.domain.model

import java.time.LocalDateTime

data class EventItem(
    val content: String,
    val created_at: LocalDateTime,
    val date: LocalDateTime,
    val id: Int,
    val images: List<Any>,
    val is_liked: Boolean,
    val post_link: String,
    val source: Int,
    val title: String
)