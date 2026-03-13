package com.pydispatch.pydispatch_mobile

import android.content.Context
import android.media.AudioManager
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val CHANNEL = "com.pydispatch/audio"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "setAlarmVolumeMax" -> {
                        try {
                            val audioManager =
                                getSystemService(Context.AUDIO_SERVICE) as AudioManager
                            // ALARM-Stream auf Maximum
                            val maxAlarm =
                                audioManager.getStreamMaxVolume(AudioManager.STREAM_ALARM)
                            val prevAlarm =
                                audioManager.getStreamVolume(AudioManager.STREAM_ALARM)
                            audioManager.setStreamVolume(
                                AudioManager.STREAM_ALARM,
                                maxAlarm,
                                0 // keine UI anzeigen
                            )
                            // MUSIC-Stream ebenfalls auf Maximum (Fallback,
                            // falls AudioContext nicht greift und Audio über
                            // den MUSIC-Stream ausgegeben wird)
                            val maxMusic =
                                audioManager.getStreamMaxVolume(AudioManager.STREAM_MUSIC)
                            val prevMusic =
                                audioManager.getStreamVolume(AudioManager.STREAM_MUSIC)
                            audioManager.setStreamVolume(
                                AudioManager.STREAM_MUSIC,
                                maxMusic,
                                0
                            )
                            result.success(mapOf(
                                "prevAlarm" to prevAlarm,
                                "prevMusic" to prevMusic
                            ))
                        } catch (e: Exception) {
                            result.error("ALARM_VOL", e.message, null)
                        }
                    }
                    "restoreAlarmVolume" -> {
                        try {
                            val audioManager =
                                getSystemService(Context.AUDIO_SERVICE) as AudioManager
                            val alarmVol = call.argument<Int>("alarmVolume") ?: call.argument<Int>("volume") ?: 0
                            val musicVol = call.argument<Int>("musicVolume")
                            audioManager.setStreamVolume(
                                AudioManager.STREAM_ALARM,
                                alarmVol,
                                0
                            )
                            if (musicVol != null) {
                                audioManager.setStreamVolume(
                                    AudioManager.STREAM_MUSIC,
                                    musicVol,
                                    0
                                )
                            }
                            result.success(true)
                        } catch (e: Exception) {
                            result.error("ALARM_VOL", e.message, null)
                        }
                    }
                    "getAlarmVolume" -> {
                        try {
                            val audioManager =
                                getSystemService(Context.AUDIO_SERVICE) as AudioManager
                            val vol =
                                audioManager.getStreamVolume(AudioManager.STREAM_ALARM)
                            val maxVol =
                                audioManager.getStreamMaxVolume(AudioManager.STREAM_ALARM)
                            result.success(mapOf("current" to vol, "max" to maxVol))
                        } catch (e: Exception) {
                            result.error("ALARM_VOL", e.message, null)
                        }
                    }
                    else -> result.notImplemented()
                }
            }
    }
}
