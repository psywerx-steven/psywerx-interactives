# RDS application binding schema specification

A binding fixes application context without redefining construct or method. Its immutable identity is `bindingId + bindingVersion`, and it anchors the exact RDS and profile versions/hashes. Applicable dimensions include population, jurisdiction, organization, network boundary, node set, tie relation, instrument, source, windows, unit, scenario state and parameters. Different context with the same computation uses a new or revised binding; method changes are prohibited in bindings.
