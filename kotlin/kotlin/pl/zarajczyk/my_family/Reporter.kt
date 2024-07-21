package pl.zarajczyk.my_family

import org.springframework.stereotype.Service

@Service
class Reporter {

    fun report(usage: Usage): Command {
        return LockScreen
    }

}

sealed interface Command
data object DoNothing : Command
data object LockScreen : Command