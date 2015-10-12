.[keys[0]] |
map(
	if has("Tags") then
		. += ( .Tags | map( { "Tag\(.Key)": (.Value) } ) | add) | del(.Tags)
	else
		.
	end
)
