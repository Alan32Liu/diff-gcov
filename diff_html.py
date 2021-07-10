import re
import os
import pdb
import sys

BODY_START = 301
BODY_END = 14637
BLANK_LINE = '<tr>' \
             '<td align="right" class="lineno"><pre> </pre></td>' \
             '<td align="right" class="linebranch"></td><td align="right" class="linecount "><pre></pre></td>' \
             '<td align="left" class="src "><pre> </pre></td>' \
             '</tr>'

LINE_NUM_PATTERN = r'<td align="right" class="lineno"><pre>(\d*)</pre></td>'

LINE_INFO_PATTERN = r'<td align="right" class="linebranch">(.*?)</td>\s*' \
                    r'<td align="right" class="linecount (\w*)"><pre>(\d*)</pre></td>'

BRANCH_INFO_PATTERN = r'(<span class="(\w*)" title="(.*?)">.*?</span>)'
BRANCH_COUNT_PATTERN = r'taken (\d+) times'

BRANCHES_SCAFFOLD = '<span class="{}" title="{}">{}</span>'
BRANCH_TAKEN_SCAFFOLD = 'Branch {} taken {} times'
BRANCH_UNTAKEN_SCAFFOLD = 'Branch {} not taken'
LINE_SCAFFOLD = '<td align="right" class="linebranch">{}</td>\n\t\t' \
                '<td align="right" class="linecount {}"><pre>{}</pre></td>'

ALL_HEADER = {}
ALL_CONTENT = {}
ALL_TAIL = {}
HTML_PATH = "/cov_html/index.ftpserv.c.html"


def collect_html():
    return [f'{fuzzer_result.name}' + HTML_PATH
            for fuzzer_result in os.scandir(result_directory)
            if fuzzer_result.is_dir()]


def parse_html(target_html):

    with open(target_html, "r") as target_file:
        all_content = list(target_file.readlines())
        target_header = all_content[:BODY_START]
        target_content = all_content[BODY_START:BODY_END]
        target_tail = all_content[BODY_END:]
    return target_header, target_content, target_tail


def preprocess_content(target_content):

    def parse_cur_line_num(cur_line):
        return int(re.search(LINE_NUM_PATTERN, cur_line).group(1))

    def parse_cur_line_info(cur_line):
        branches_info, line_info, cover_count = re.search(LINE_INFO_PATTERN, cur_line).groups()

        branches_cov = tuple((branch_info[1] == 'takenBranch',
                              int(re.search(BRANCH_COUNT_PATTERN, branch_info[2]).group(1))
                              if branch_info[1] == 'takenBranch' else 0,
                              branch_info[0])
                             for branch_info in re.findall(BRANCH_INFO_PATTERN, branches_info))

        line_cov = line_info == "coveredLine"
        cover_count = int(cover_count) if cover_count else 0

        # branch_stat = tuple(branch_cov for branches_cov)
        # for branch_cov in branches_cov:
        #
        #     if not branch_cov:
        #         continue



        return branches_cov, line_cov, cover_count, cur_line

    target_dict = {
        parse_cur_line_num(cur_line): parse_cur_line_info(cur_line)
        for cur_line in re.findall(r"(.*?)\n\n", "".join(target_content), re.DOTALL)
    }
    return target_dict


def compare_html():

    max_lines = [len(ALL_CONTENT[fuzzer][i]) for i in range(max_instance) for fuzzer in ['aflnet', 'legion']]
    assert all([max_lines[0] == max_line for max_line in max_lines])

    result_lines = []
    for line_num in range(1, max_lines[0]+1):
        fuzzer_sumary = {'aflnet': None, 'legion': None}
        result_line = {'aflnet': None, 'legion': None}
        for fuzzer in ['aflnet', 'legion']:
            assert ALL_CONTENT[fuzzer][0]
            line_cov = ALL_CONTENT[fuzzer][0][line_num][1]
            line_cov_count = [ALL_CONTENT[fuzzer][0][line_num][2]]
            line_info = ALL_CONTENT[fuzzer][0][line_num][3]
            branches_stat = ALL_CONTENT[fuzzer][0][line_num][0]

            for instance_num in range(1, max_instance):
                line_cov_count.append([ALL_CONTENT[fuzzer][instance_num][line_num][2]])
                if ALL_CONTENT[fuzzer][instance_num][line_num][1] > line_cov:
                    line_cov = ALL_CONTENT[fuzzer][instance_num][line_num][1]
                    line_info = ALL_CONTENT[fuzzer][instance_num][line_num][3]
                for i, branch_stat in enumerate(ALL_CONTENT[fuzzer][instance_num][line_num][0]):

                    if not branch_stat:
                        continue
                    if not branches_stat:
                        branches_stat = ALL_CONTENT[fuzzer][instance_num][line_num][0]
                        continue
                    if branch_stat[0] > branches_stat[i][0] or branch_stat[1] > branches_stat[i][1]:
                        branches_stat = list(branches_stat)
                        branches_stat[i] = tuple(branch_stat)
                        branches_stat = tuple(branches_stat)

            BRANCHES_SCAFFOLD = '<span class="{}" title="{}">{}</span>'
            BRANCH_TAKEN_SCAFFOLD = 'Branch {} taken {} times'
            BRANCH_UNTAKEN_SCAFFOLD = 'Branch {} not taken'
            LINE_SCAFFOLD = '<td align="right" class="linebranch">{}</td>'

            merged_branches = ""
            for i, branch_stat in enumerate(branches_stat):
                merged_branches += BRANCHES_SCAFFOLD.format(
                    "takenBranch" if branch_stat[0] else "notTakenBranch",
                    BRANCH_TAKEN_SCAFFOLD.format(i, branches_stat[i][1])
                    if branch_stat[0] else BRANCH_UNTAKEN_SCAFFOLD.format(i),
                    "&check;" if branch_stat[0] else "&cross;"
                )
            branch_in_line = LINE_SCAFFOLD.format(merged_branches)
            line_info = line_info.split('    ')
            line_info[3] = branch_in_line
            line_formatted = '    '.join(line_info)
            result_line[fuzzer] = line_formatted
            fuzzer_sumary[fuzzer] = [line_cov] + [branch_stat[0] for branch_stat in branches_stat]

        # if not fuzzer_sumary['aflnet']:
        #     pdb.set_trace()
        # if (fuzzer_sumary['aflnet'] or fuzzer_sumary['legion']) and not (fuzzer_sumary['aflnet'] and fuzzer_sumary['legion']):
        #     pdb.set_trace()

        # if len(fuzzer_sumary['aflnet']) != len(fuzzer_sumary['legion']):
        #     pdb.set_trace()

        assert (not fuzzer_sumary['aflnet'] and not fuzzer_sumary['legion']) \
               or (not fuzzer_sumary['aflnet'][0] or not fuzzer_sumary['legion'][0]) \
               or (len(fuzzer_sumary['aflnet']) == len(fuzzer_sumary['legion']))
        # print(fuzzer_sumary['aflnet'], fuzzer_sumary['legion'])
        if fuzzer_sumary['aflnet'] == fuzzer_sumary['legion']:
            continue

        result_lines.append(result_line['aflnet'])
        result_lines.append(result_line['legion'])
        result_lines.append(BLANK_LINE)

            # aflnet_branch_cov, aflnet_line_cov = re.search(block_pattern, aflnet_dict[line_number], re.DOTALL).groups()
        # legion_branch_cov, legion_line_cov = re.search(block_pattern, legion_dict[line_number], re.DOTALL).groups()
        #
        # if aflnet_line_cov != legion_line_cov:
        #     result_content.append(aflnet_dict[line_number])
        #     result_content.append(legion_dict[line_number])
        #     result_content.append(BLANK_LINE)
        #     continue
        #
        # if (aflnet_branch_cov or legion_branch_cov) \
        #         and re.findall(branch_pattern, aflnet_branch_cov) != re.findall(branch_pattern, legion_branch_cov):
        #     result_content.append(aflnet_dict[line_number])
        #     result_content.append(legion_dict[line_number])
        #     result_content.append(BLANK_LINE)

    return result_lines


def construct_result():
    with open(result_html, "w") as target_file:
        target_file.writelines(ALL_HEADER['aflnet'][0] + result_content + ALL_TAIL['aflnet'][0])


if __name__ == '__main__':
    result_directory = sys.argv[1]
    result_html = "comparison_aflnet_legion.html"
    all_hthml = collect_html()
    max_instance = max(int(each_html.split("/")[0].split("-")[-1]) for each_html in all_hthml)
    ALL_HEADER = {'aflnet': [None] * max_instance, 'legion': [None] * max_instance}
    ALL_CONTENT = {'aflnet': [None] * max_instance, 'legion': [None] * max_instance}
    ALL_TAIL = {'aflnet': [None] * max_instance, 'legion': [None] * max_instance}

    for each_html in collect_html():
        fuzzer, instance = each_html.split("/")[0].split("-")
        fuzzer = fuzzer.split("_")[-1]
        instance = int(instance)
        ALL_HEADER[fuzzer][instance-1], content, ALL_TAIL[fuzzer][instance-1] \
            = parse_html(each_html)
        ALL_CONTENT[fuzzer][instance-1] = preprocess_content(content)

    # print(ALL_CONTENT['legion'][0][109])

    result_content = compare_html()
    # print(result_content)

    construct_result()

