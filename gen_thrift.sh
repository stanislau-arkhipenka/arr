#!/bin/bash

thrift --gen py --out ./steam_deck/ ./spec.thrift
thrift --gen py --out ./acp/ ./spec.thrift

mv ./steam_deck/spec/ARR_proto-remote ./steam_deck/