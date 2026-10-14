# Do not import `.router` here: it re-exports app.intelligence.api.news, which
# imports this package's feed_manager, so an eager import creates a cycle that
# stops app.main from loading. Import app.domain.intelligence.router directly.
