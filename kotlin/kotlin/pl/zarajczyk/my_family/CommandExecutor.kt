package pl.zarajczyk.my_family

import com.lordcodes.turtle.shellRun
import org.springframework.stereotype.Service

@Service
class CommandExecutor {

    fun execute(command: Command) = when (command) {
        is DoNothing -> doNothing()
        is LockScreen -> showLockScreen()
    }

    private fun doNothing() {
        // nothing
    }

    private fun showLockScreen() {
        shellRun("bash", listOf("-c", "/Users/rafal/Developer/my-family/src/main/resources/scripts/mac/lock-screen.sh"))
    }

}