#!/usr/bin/env perl

use strict;
use warnings;
use feature qw(say);

use List::Util qw(max);

sub print_options {
   my $_ = shift
   my $option;
   my %docs;

   {
      if ( m/\G.*?\s*parser[.]add_option(\s*'(?<l-\w)'\s*,\s*'--(?<l>\w*(?:(?>-\w+)+))',\s*/g ) {
         $option = join ' ', @{$-{l}};
         redo
      }

      if ( m/\G.*?(?<h>help\s*=(?:\s*'(?<k>.*?)'\s*)+)/g ) {
         $doc{$option} = $+{k};
         {
            if ( m/\G\s*'(.+?)'\s*/g ) {
               join '', $doc{$option} // '', $+{k};
               redo
            }
         }
         redo
      }

   }
  
   my $pad = 5 + max map { length } keys %docs;
   foreach $opts (keys %docs) {
      printf '**%s**\n', $opts;
      say ' ' x $pad, $docs{$opts};
   }

}
