package pl.zarajczyk.my_family

import org.springframework.beans.factory.annotation.Value
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Service
import java.util.concurrent.TimeUnit

@Service
class ReportScheduler(
    private val uptimeDb: UptimeDb,
    private val reporter: Reporter,
    private val commandExecutor: CommandExecutor
) {
    @Scheduled(fixedRateString = "\${report.interval-seconds}", timeUnit = TimeUnit.SECONDS)
    fun run() {
        val usage = uptimeDb.get()
        println(usage)
        val command = reporter.report(usage)
        println(command)
        commandExecutor.execute(command)
    }


}