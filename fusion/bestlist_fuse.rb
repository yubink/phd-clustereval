#! /bos/usr0/yubink/bin/ruby -I /bos/usr0/yubink/rubylib  -I .

#creates a gold standard fused result list by picking the best performing
#query (using qrels) from a list of input result lists

require 'optparse'
require 'slidefuse'
require 'irmetrics'


$options = {}

op = OptionParser.new do |opts|
  opts.banner = """Usage ./bestlist_fuse.rb [options] [rank list files] ...
  Creates a result set using the best queries of a given rank list files"""

#  opts.on("-w", "--window NUM", Integer, "Window size param for SlideFuse") do |x|
#    $options[:window] = x
#  end
#
#  opts.on("-o", "--output DIR", "Output directory") do |f|
#    $options[:outdir] = f
#  end

  opts.on("-q", "--qrels FILE", "File containing qrels") do |f|
    $options[:qrels] = f
  end

  opts.on("-m", "--metric METRIC", "Metric to use to decide \"best\"") do |f|
    $options[:metric] = f
  end
end

op.parse!

all_lists = []
for rankfile in ARGV
  name = File.basename(rankfile)

  map_vals = Hash.new
  File.open(rankfile + ".Qeval") do |f|
    for line in f
      if line.start_with?("#{$options[:metric]} ")
        metric, qnum, val = line.split
        if qnum != "all"
          map_vals[qnum] = val.to_f
        end
      end
    end
  end

  results = nil
  File.open(rankfile) do |f|
    results = IRMetrics.load_all_results(f)
  end

  all_lists << [results, map_vals]
end

$stderr.puts "read all"

for qnum in all_lists[0][1].keys
  max_list = nil
  max_score = 0

  for list in all_lists
    if list[1][qnum] > max_score
      max_score = list[1][qnum]
      max_list = list[0][qnum]
    end
  end

  puts max_list[0...1000]
end
