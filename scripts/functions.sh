#!/usr/bin/env bash
# These should work with both bash and zsh
#
# To use these, put 'source /path/to/this/repo/functions.sh'
# in your shell profile
#
# these use a bunch of common-ish shell tools
# to interact with the hpi query JSON API
# jq: https://github.com/stedolan/jq
# fzf: https://github.com/junegunn/fzf

# helpers used across multiple functions
alias mpv-from-stdin='mpv --playlist=- --no-audio-display --msg-level=file=error'
filter_unique() {
	awk '!seen[$0]++'
}

###################
# my.listenbrainz
###################

scrobbles() {
	hpi query my.listenbrainz.export.history -s "$@"
}
scrobble-describe() {
	jq -r '"\(.listened_at) \(.artist_name) - \(.track_name)"'
}

##########
# my.mpv
##########

# functions to replay music I've listened to recently
mpv-recent() {
	local args=()
	if [[ -n "$1" ]]; then
		args+=("--limit" "$1")

	fi
	hpi query my.mpv.history_daemon.history --order-type datetime --reverse -s "${args[@]}"
}
mpv-recent-path() {
	mpv-recent "$1" | jq -r .path
}
replay() {
	mpv-recent-path | exists | grep --max-count=1 "$XDG_MUSIC_DIR" | mpv-from-stdin
}
# requires https://github.com/purarue/exists, https://github.com/purarue/pura-utils
replay-recent() {
	mpv-recent-path "$1" | exists | unique | head -n "${1:-$LINES}" | fzf --select-1 | mpv-from-stdin
}

##########
# my.zsh
##########

# jq later to preserve newlines in commands
alias zsh-unique="hpi query -s my.zsh.history | jq '.command' | filter_unique | jq -r"
alias zsh-unique-fzf='zsh-unique | fzf'

############
# my.trakt
############

# e.g. trakt-movies --recent 4w | trakt-describe-movie
trakt-movies() {
	hpi query 'my.trakt.export.history' -s "$@" | trakt-filter-movies
}

# e.g. trakt-episodes --recent 4w | trakt-describe-episode
trakt-episodes() {
	hpi query 'my.trakt.export.history' -s "$@" | trakt-filter-episodes
}

trakt-filter-movies() {
	jq 'select(.media_type == "movie")'
}

trakt-filter-episodes() {
	jq 'select(.media_type == "episode")'
}

trakt-describe-movie() {
	jq -r '"\(.media_data.title) (\(.media_data.year))"'
}

trakt-describe-episode() {
	jq -r '"\(.media_data.show.title) (\(.media_data.show.year)) - S\(.media_data.season)E\(.media_data.episode) \(.media_data.title)"'
}

trakt-recent-episodes() {
	traktexport partial_export purplepinapples --pages 1 2>/dev/null | jq '.history | .[] | select(.type == "episode") | "https://trakt.tv/shows/\(.show.ids.slug)/\(.episode.season)/\(.episode.number)"' -r
}
