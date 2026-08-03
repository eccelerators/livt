#!/usr/bin/env bash

set -uo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
project_dir=$(cd -- "${script_dir}/.." && pwd)
livt_command=${LIVT:-livt}
report_dir="${project_dir}/.livt/reports/standard-library"
temporary_dir=$(mktemp -d "${TMPDIR:-/tmp}/livt-standard-library.XXXXXX")
failures=()
tested_packages=0
declare -A pinned_dependencies=()

cleanup() {
	chmod -R u+w "${temporary_dir}" 2>/dev/null || true
	rm -rf -- "${temporary_dir}"
}
trap cleanup EXIT

record_failure() {
	failures+=("$1")
}

load_pinned_dependencies() {
	local line
	local dependency
	local version

	while IFS= read -r line; do
		dependency=${line%%=*}
		version=${line#*=}
		dependency=${dependency//[[:space:]]/}
		version=${version//[[:space:]\"]/}
		pinned_dependencies["${dependency}"]=${version}
	done < <(awk '
		$0 == "[dependencies]" { in_dependencies = 1; next }
		in_dependencies && /^\[/ { exit }
		in_dependencies && /^[[:space:]]*[[:alnum:]_.-]+[[:space:]]*=/ { print }
	' "${project_dir}/livt.toml")
}

apply_pinned_dependencies() {
	local manifest=$1
	local dependency
	local escaped_dependency
	local pinned_version

	for dependency in "${!pinned_dependencies[@]}"; do
		escaped_dependency=${dependency//./\\.}
		pinned_version=${pinned_dependencies[${dependency}]}
		sed -i -E \
			"s|^([[:space:]]*${escaped_dependency}[[:space:]]*=[[:space:]]*)\"[^\"]*\"|\\1\"${pinned_version}\"|" \
			"${manifest}"
	done
}

load_pinned_dependencies

echo "Synchronizing the Livt standard-library package set..."
if ! "${livt_command}" sync --project "${project_dir}"; then
	echo "Could not synchronize the Livt package set." >&2
	exit 1
fi

mkdir -p "${report_dir}"

while IFS= read -r -d '' package_dir; do
	package_id=$(basename -- "${package_dir}")
	writable_package="${temporary_dir}/${package_id}"
	report_name=$(printf '%s' "${package_id}" | tr '/ ' '__')
	tested_packages=$((tested_packages + 1))

	echo
	echo "Testing ${package_id}..."
	cp -R -- "${package_dir}" "${writable_package}"
	chmod -R u+rwX "${writable_package}"

	if [[ ! -f "${writable_package}/livt.toml" ]]; then
		record_failure "${package_id}: package manifest is missing"
		continue
	fi
	apply_pinned_dependencies "${writable_package}/livt.toml"
	if ! grep -q '^\[tests\]$' "${writable_package}/livt.toml"; then
		record_failure "${package_id}: no test suite is configured"
		continue
	fi
	if ! (
		cd -- "${writable_package}"
		"${livt_command}" sync --project .
	); then
		record_failure "${package_id}: dependency synchronization failed"
		continue
	fi
	if ! (
		cd -- "${writable_package}"
		"${livt_command}" test --project . \
			--junit "${report_dir}/${report_name}.xml"
	); then
		record_failure "${package_id}: tests failed"
	fi
done < <(find "${project_dir}/.livt/deps" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)

if (( tested_packages == 0 )); then
	record_failure "No synchronized Livt packages were found"
fi

echo
echo "Testing the combined Livt package set..."
if ! (
	cd -- "${project_dir}"
	"${livt_command}" test --project . --junit "${report_dir}/Livt.xml"
); then
	record_failure "Livt: combined compatibility tests failed"
fi

echo
if (( ${#failures[@]} > 0 )); then
	echo "Standard-library verification failed:" >&2
	for failure in "${failures[@]}"; do
		echo "- ${failure}" >&2
	done
	echo "JUnit reports: ${report_dir}" >&2
	exit 1
fi

echo "Standard-library verification passed for ${tested_packages} packages and the combined Livt project."
echo "JUnit reports: ${report_dir}"
