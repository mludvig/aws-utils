# Right-pad string with spaces
def pad(width):
  tostring | if width > length then . + (width - length) * " " else . end;

# Display running instances' Name and PrivateIpAddress
[
	.Reservations[].Instances[0]
	| select(.State.Name == "running" and .Tags != null)
	| {
		"PrivateIpAddress": .PrivateIpAddress?,
		"Name": .Tags[] | select(.Key == "Name") | .Value,
	}
]
| sort_by(.Name)
| .[] 
| @text "\(.Name | pad(20))     \(.PrivateIpAddress)"
