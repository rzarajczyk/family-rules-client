package pl.zarajczyk.my_family

import org.springframework.beans.factory.annotation.Value
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Service
import java.util.concurrent.TimeUnit

@Service
class CheckAppsScheduler(
    private val runningApplicationsFetcher: RunningApplicationsFetcher,
    private val uptimeDb: UptimeDb,
    @Value("\${usage.check-interval-seconds}") private val checkIntervalSeconds: Int
) {
    @Scheduled(fixedRateString = "\${usage.check-interval-seconds}", timeUnit = TimeUnit.SECONDS)
    fun run() {
        val apps = runningApplicationsFetcher.getRunningApps()
        uptimeDb.update(apps, checkIntervalSeconds)
    }


}