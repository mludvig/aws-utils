#!/usr/bin/env bats

# Test suite for filter-ip-ranges

BINARY="./filter-ip-ranges"
COMMAND="${BINARY} --quiet --file tests/filter-ip-ranges.ip-ranges"

@test "PyLint the source" {
    run pylint -E ${BINARY}
    [ "$status" -eq 0 ]
}

# ===== Without --ipv4/--ipv6 =====

@test "List all prefixes" {
  result="$(${COMMAND} | wc -l)"
  [ "$result" -eq 1068 ]
}

@test "List prefixes in ap-southeast-2" {
  result="$(${COMMAND} ap-southeast-2 | wc -l)"
  [ "$result" -eq 51 ]
}

@test "List prefixes in ap-southeast-2 that are S3" {
  result="$(${COMMAND} ap-southeast-2 S3 | wc -l)"
  [ "$result" -eq 8 ]
}

@test "List prefixes in ap-southeast-2 that are not S3" {
  result="$(${COMMAND} ap-southeast-2 -S3 | wc -l)"
  [ "$result" -eq 43 ]
}

@test "List prefixes in ap-southeast-2 that are S3 and EC2" {
  result="$(${COMMAND} ap-southeast-2 S3 EC2 | wc -l)"
  [ "$result" -eq 0 ]
}

@test "List prefixes that are AMAZON only" {
  result="$(${COMMAND} =AMAZON | wc -l)"
  [ "$result" -eq 378 ]
}

# ===== With --ipv4 =====

@test "List all IPv4 prefixes" {
  result="$(${COMMAND} -4 | wc -l)"
  [ "$result" -eq 806 ]
}

@test "List IPv4 prefixes in ap-southeast-2" {
  result="$(${COMMAND} --ipv4 ap-southeast-2 | wc -l)"
  [ "$result" -eq 36 ]
}

@test "List IPv4 prefixes in ap-southeast-2 that are S3" {
  result="$(${COMMAND} --ipv4 ap-southeast-2 S3 | wc -l)"
  [ "$result" -eq 4 ]
}

@test "List IPv4 prefixes in ap-southeast-2 that are not S3" {
  result="$(${COMMAND} --ipv4 ap-southeast-2 -S3 | wc -l)"
  [ "$result" -eq 32 ]
}

@test "List IPv4 prefixes in ap-southeast-2 that are S3 and EC2" {
  result="$(${COMMAND} --ipv4 ap-southeast-2 S3 EC2 | wc -l)"
  [ "$result" -eq 0 ]
}

@test "List IPv4 prefixes that are AMAZON only" {
  result="$(${COMMAND} --ipv4 =AMAZON | wc -l)"
  [ "$result" -eq 313 ]
}

@test "Look up IPv4 host address" {
  result="$(${COMMAND} --ipv4 --verbose 52.95.128.255)"
  [ "$result" = "52.95.128.0/21 ap-southeast-2 AMAZON S3" ]
}

@test "Look up IPv4 network address" {
  result="$(${COMMAND} --ipv4 --verbose 52.95.128.0/24)"
  [ "$result" = "52.95.128.0/21 ap-southeast-2 AMAZON S3" ]
}

@test "Look up IPv4 host address (without --ipv4)" {
  result="$(${COMMAND} --verbose 52.95.128.255)"
  [ "$result" = "52.95.128.0/21 ap-southeast-2 AMAZON S3" ]
}

@test "Look up IPv4 network address (without --ipv4)" {
  result="$(${COMMAND} --verbose 52.95.128.0/24)"
  [ "$result" = "52.95.128.0/21 ap-southeast-2 AMAZON S3" ]
}

# ===== With --ipv6 =====

@test "List all IPv6 prefixes" {
  result="$(${COMMAND} -6 | wc -l)"
  [ "$result" -eq 262 ]
}

@test "List IPv6 prefixes in ap-southeast-2" {
  result="$(${COMMAND} --ipv6 ap-southeast-2 | wc -l)"
  [ "$result" -eq 15 ]
}

@test "List IPv6 prefixes in ap-southeast-2 that are S3" {
  result="$(${COMMAND} --ipv6 ap-southeast-2 S3 | wc -l)"
  [ "$result" -eq 4 ]
}

@test "List IPv6 prefixes in ap-southeast-2 that are not S3" {
  result="$(${COMMAND} --ipv6 ap-southeast-2 -S3 | wc -l)"
  [ "$result" -eq 11 ]
}

@test "List IPv6 prefixes in ap-southeast-2 that are S3 and EC2" {
  result="$(${COMMAND} --ipv6 ap-southeast-2 S3 EC2 | wc -l)"
  [ "$result" -eq 0 ]
}

@test "List IPv6 prefixes that are AMAZON only" {
  result="$(${COMMAND} --ipv6 =AMAZON | wc -l)"
  [ "$result" -eq 65 ]
}

@test "Look up IPv6 host address" {
  result="$(${COMMAND} --ipv6 --verbose 2406:daa0:c000::1:2:3:4)"
  [ "$result" = "2406:daa0:c000::/40 ap-southeast-2 AMAZON S3" ]
}

@test "Look up IPv6 network address" {
  result="$(${COMMAND} --ipv6 --verbose 2406:daa0:c000::64)"
  [ "$result" = "2406:daa0:c000::/40 ap-southeast-2 AMAZON S3" ]
}

@test "Look up IPv6 host address without --ipv6" {
  result="$(${COMMAND} --verbose 2406:daa0:c000::1:2:3:4)"
  [ "$result" = "2406:daa0:c000::/40 ap-southeast-2 AMAZON S3" ]
}

@test "Look up IPv6 network address without --ipv6" {
  result="$(${COMMAND} --verbose 2406:daa0:c000::64)"
  [ "$result" = "2406:daa0:c000::/40 ap-southeast-2 AMAZON S3" ]
}
