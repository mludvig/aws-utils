.Reservations[].Instances[0]
| select(.State.Name == "running")
| {
	"InstanceId": .InstanceId,
	"PrivateIpAddress": .PrivateIpAddress,
	"Name": .Tags[] | select(.Key == "Name") | .Value
}
