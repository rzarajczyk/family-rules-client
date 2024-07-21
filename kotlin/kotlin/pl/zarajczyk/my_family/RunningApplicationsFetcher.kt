package pl.zarajczyk.my_family

import com.lordcodes.turtle.shellRun
import org.apache.commons.lang3.SystemUtils
import org.springframework.stereotype.Service

@Service
class RunningApplicationsFetcher {
    fun getRunningApps(): List<String> = when {
        SystemUtils.IS_OS_MAC -> getRunningAppsMacOs()
        else -> throw RuntimeException("Unsupported operating system")
    }

    private fun getRunningAppsMacOs(): List<String> {
        val user = SystemUtils.getUserName()
        return shellRun("ps", listOf("-u $user", "-o comm"))
            .lines()
            .filter { it.startsWith("/Applications/") }
            .map { it.substring(0, it.indexOf(".app/") + 4) }
            .map { it.removePrefix("/Applications/") }
            .distinct()
            .toList()
    }
}