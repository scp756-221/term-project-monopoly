package proj756

import scala.concurrent.duration._

import io.gatling.core.Predef._
import io.gatling.http.Predef._

/*
TODO:
1. You must run your application with up to a load of thousands of users (e.g, >1000 users) and hundreds of thousands requests (e.g., >100,00 requests/second).
2. Other tests besides just reading from the table
*/


object Utility {
  /*
    Utility to get an Int from an environment variable.
    Return defInt if the environment var does not exist
    or cannot be converted to a string.
  */
  def envVarToInt(ev: String, defInt: Int): Int = {
    try {
      sys.env(ev).toInt
    } catch {
      case e: Exception => defInt
    }
  }

  /*
    Utility to get an environment variable.
    Return defStr if the environment var does not exist.
  */
  def envVar(ev: String, defStr: String): String = {
    sys.env.getOrElse(ev, defStr)
  }
}

/*
  Read music
*/
object RMusic {

  val feeder = csv("music.csv").eager.random

  val rmusic = forever("i") {
    feed(feeder)
    .exec(http("RMusic ${i}")
      .get("/api/v1/music/${UUID}"))
      .pause(Utility.envVarToInt("PAUSE_MILLI", 1000).millis)
  }

}

/*
  Read user
*/
object RUser {

  val feeder = csv("users.csv").eager.circular

  val ruser = forever("i") {
    feed(feeder)
    .exec(http("RUser ${i}")
      .get("/api/v1/user/${UUID}"))
    .pause(Utility.envVarToInt("PAUSE_MILLI", 1000).millis)
  }

}

/*
  Read playlist
*/
object RPlaylist {

  val feeder = csv("playlist.csv").eager.circular

  val rplaylist = forever("i") {
    feed(feeder)
    .exec(http("RPlaylist ${i}")
      .get("/api/v1/playlist/${UUID}"))
    .pause(Utility.envVarToInt("PAUSE_MILLI", 1000).millis)
  }

}

/*
  After one S1 read, pause a random time between 1 and 60 s
*/
object RUserVarying {
  val feeder = csv("users.csv").eager.circular

  val ruser = forever("i") {
    feed(feeder)
    .exec(http("RUserVarying ${i}")
      .get("/api/v1/user/${UUID}"))
    .pause(1, 60)
  }
}

/*
  After one S2 read, pause a random time between 1 and 60 s
*/

object RMusicVarying {
  val feeder = csv("music.csv").eager.circular

  val rmusic = forever("i") {
    feed(feeder)
    .exec(http("RMusicVarying ${i}")
      .get("/api/v1/music/${UUID}"))
    .pause(1, 60)
  }
}

/*
  After one S3 read, pause a random time between 1 and 60 s
*/

object RPlaylistVarying {
  val feeder = csv("playlist.csv").eager.circular

  val rplaylist = forever("i") {
    feed(feeder)
    .exec(http("RPlaylistVarying ${i}")
      .get("/api/v1/playlist/${UUID}"))
    .pause(1, 60)
  }
}

/*
  Failed attempt to interleave reads from User, Music, Playlist tables.
  The Gatling EDSL only honours the second (Music) read,
  ignoring the first read of User. [Shrug-emoji] 
 */
object RBoth {

  val u_feeder = csv("users.csv").eager.circular
  val m_feeder = csv("music.csv").eager.random
  val p_feeder = csv("playlist.csv").eager.random

  val rboth = forever("i") {
    feed(u_feeder)
    .exec(http("RUser ${i}")
      .get("/api/v1/user/${UUID}"))
    .pause(1);

    feed(m_feeder)
    .exec(http("RMusic ${i}")
      .get("/api/v1/music/${UUID}"))
    .pause(1);

    feed(p_feeder)
    .exec(http("RPlaylist ${i}")
      .get("/api/v1/playlist/${UUID}"))
    .pause(1);
  }

}

// Get Cluster IP from CLUSTER_IP environment variable or default to 127.0.0.1 (Minikube)
class ReadTablesSim extends Simulation {
  val httpProtocol = http
    .baseUrl("http://" + Utility.envVar("CLUSTER_IP", "127.0.0.1") + "/")
    .acceptHeader("application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    .authorizationHeader("Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZGJmYmMxYzAtMDc4My00ZWQ3LTlkNzgtMDhhYTRhMGNkYTAyIiwidGltZSI6MTYwNzM2NTU0NC42NzIwNTIxfQ.zL4i58j62q8mGUo5a0SQ7MHfukBUel8yl8jGT5XmBPo")
    .acceptLanguageHeader("en-US,en;q=0.5")
}

class ReadUserSim extends ReadTablesSim {
  val scnReadUser = scenario("ReadUser")
      .exec(RUser.ruser)

  setUp(
    scnReadUser.inject(atOnceUsers(Utility.envVarToInt("USERS", 1)))
  ).protocols(httpProtocol)
}

class ReadMusicSim extends ReadTablesSim {
  val scnReadMusic = scenario("ReadMusic")
    .exec(RMusic.rmusic)

  setUp(
    scnReadMusic.inject(atOnceUsers(Utility.envVarToInt("USERS", 1)))
  ).protocols(httpProtocol)
}

class ReadPlaylistSim extends ReadTablesSim {
  val scnReadPlaylist = scenario("ReadPlaylist")
    .exec(RPlaylist.rplaylist)

  setUp(
    scnReadPlaylist.inject(atOnceUsers(Utility.envVarToInt("USERS", 1)))
  ).protocols(httpProtocol)
}

/*
  Read all services concurrently at varying rates.
  Ramp up new users one / 10 s until requested USERS
  is reached for each service.
*/
class ReadAllSim extends ReadTablesSim {
  val scnReadMusic = scenario("ReadMusic")
    .exec(RMusic.rmusic)
  
  val scnReadPlaylist = scenario("ReadPlaylist")
    .exec(RPlaylist.rplaylist)

  val scnReadUser = scenario("ReadUse")
    .exec(RUser.ruser)

  val users = Utility.envVarToInt("USERS", 1)

  setUp(
    // Add one user per 10 s up to specified value
    scnReadUser.inject(atOnceUsers(Utility.envVarToInt("USERS", 1))),
    scnReadMusic.inject(atOnceUsers(Utility.envVarToInt("USERS", 1))),
    scnReadPlaylist.inject(atOnceUsers(Utility.envVarToInt("USERS", 1)))
  ).protocols(httpProtocol)
}

class ReadAllVaryingSim extends ReadTablesSim {
  val scnReadMV = scenario("ReadMusicVarying")
    .exec(RMusicVarying.rmusic)
  
  val scnReadPV = scenario("ReadPlaylistVarying")
    .exec(RPlaylistVarying.rplaylist)

  val scnReadUV = scenario("ReadUserVarying")
    .exec(RUserVarying.ruser)

  val users = Utility.envVarToInt("USERS", 10)

  setUp(
    // Add one user per 10 s up to specified value
    scnReadMV.inject(rampConcurrentUsers(1).to(users).during(10*users)),
    scnReadPV.inject(rampConcurrentUsers(1).to(users).during(10*users)),
    scnReadUV.inject(rampConcurrentUsers(1).to(users).during(10*users))
  ).protocols(httpProtocol)
}

/*
  This doesn't work---it just reads the Music table.
  We left it in here as possible inspiration for other work
  (or a warning that this approach will fail).
 */
/*
class ReadAllSim extends ReadTablesSim {
  val scnReadAll = scenario("ReadAll")
    .exec(RAll.rall)
  setUp(
    scnReadAll.inject(atOnceUsers(1))
  ).protocols(httpProtocol)
}
*/