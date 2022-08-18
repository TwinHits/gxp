
class Queries:

    GET_REPORTS_BY_GUILD = """query ($page: Int) {
        guildData {
            guild(id: 608268) {
                attendance(page: $page, , limit: 25) {
                    has_more_pages
                    data {
                        code
                        startTime
                        zone {
                            name
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
                endTime,
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
				startTime,
                endTime,
                fights(killType:Kills) {
                    friendlyPlayers,
                    name,
					endTime
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


    GET_PERFORMANCE_BY_REPORT_ID = """query ($code: String) {
            reportData {
                report(code: $code) {
                    rankings
                }
            }
        } 
    """