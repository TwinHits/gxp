
class Queries:

    GET_RAIDS_BY_GUILD_ID = """query ($page: Int) {
        guildData {
            guild(id: 608268) {
                id
                name
                attendance(page: $page) {
                    has_more_pages
                    data {
                        code
                        startTime
                        zone {
                            name
                        }
                        players {
                            name
                            presence
                        }
                    }
                }
            }
        }
    }"""


    GET_RAID_BY_REPORT_ID = """query ($code: String) {
        reportData {
            report(code: $code) {
                startTime,
                zone {
                    name
                },
                fights(killType:Kills) {
                    friendlyPlayers,
                    name
                },
                rankedCharacters {
                    id,
                    name
                },
                masterData {
                    actors(type:"Player") {
                        id,
                        name
                    }
                }
            }
        }
    }"""

    GET_RAID_KILLS_BY_REPORT_ID = """query ($code: String) {
        reportData {
            report(code: $code) {
                fights(killType:Kills) {
                    friendlyPlayers,
                    name
                },
                masterData {
                    actors(type:"Player") {
                        id,
                        name
                    }
                }
            }
        }
    }"""