# aws-utils

`aws-utils` is a collection of useful tools for AWS, mainly for users
of *aws cli*.

New scripts are added every now and then, whenever I need
and develop one.

They usually support `--help`, often with usage examples. If not check
the source :)

## aws-utils scripts

* **[ssm-session](ssm-session)**

    Convenience wrapper around `aws ssm start-session` that can open
    SSM Session to an instance specified by Name or IP Address.

* **get-credentials**

* **get-instance-credentials**

* **assume-role**

* **filter-ip-ranges**

* **crawl-metadata**

* **find-ami**

## Author and License

All these scripts were written by [Michael Ludvig](https://aws.nz/)
and are released under [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0).
